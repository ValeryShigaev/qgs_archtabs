from qgis.core import (QgsProject, QgsPoint, QgsFeature, QgsGeometry,
                       QgsVectorLayer, QgsField, QgsExpression,
                       QgsExpressionContext, edit, QgsExpressionContextUtils,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                       QgsFeatureRequest)
from qgis.PyQt.QtCore import QVariant
from typing import Dict, List, Union
from .decorators import error_handler


class DataHandler:
    """
    This class contains plugin logic.

    Args:
        self.bound_data: template of a dict from which border data will
        be written
        self.coord_data: template of a dict from which coordinates data will
        be written
        self.landmarks_data: template of a dict from which landmarks data will
        be written
        self.land_str: dict of units on different languages
        self.direction: Qgis expression to calculate azimuth
        self.length: Qgis expression to calculate length
        self.x: Qgis expression to calculate x
        self.y: Qgis expression to calculate y
        self.eng: option of description in english
    """

    def __init__(self) -> object:
        self.bound_data = {"From": list(), "To": list(), "Desc": list(),
                           "Az": list(), "Len": list()}
        self.coord_data = {"Nm": list(), "X": list(), "Y": list(),
                           "X1": list(), "Y1": list()}
        self.landmarks_data = {"Nm": list(), "Az": list(), "Len": list()}
        self.land_str = {"Deutsch": ["m", "az"],
                         "English": ["m", "az"],
                         "Russian": ["м", "аз"]}
        self.direction = QgsExpression("degrees(azimuth( start_point"
                                       "( $geometry ), end_point("
                                       "$geometry )))")
        self.length = QgsExpression("$length")
        self.x = QgsExpression('$x')
        self.y = QgsExpression('$y')
        self.de = "Ein Segment der Grenze, {}m, verläuft in Richtung {} "\
                  "entlang {}"
        self.eng = "A segment of the border with a length of {}m runs in the"\
                   " direction of the {} along {}"
        self.ru = "Отрезок границы, протяженностью {}м проходит в направлении"\
                  " {} по {}"

    def clear_data(self) -> None:
        """ This method clears some objects dicts """

        self.landmarks_data = {"Nm": list(), "Az": list(), "Len": list()}
        self.coord_data = {"Nm": list(), "X": list(), "Y": list(),
                           "X1": list(), "Y1": list()}
        self.bound_data = {"From": list(), "To": list(), "Desc": list(),
                           "Az": list(), "Len": list()}

    @error_handler("Landmarks handler")
    def landmarks_handler(self, values: Dict[str, any]) -> None:
        """
        This method handles landmarks data and write it in output field
        self.landmarks_data. It creates a new layer which will added to
        project.

        :param values: dict of interface data
        :type values: Dict[str, any]
        """

        if values.get("landmarks") and values.get("benchmark"):
            benchmark = values["benchmark"]
            benchmark.setCrs(values["crs"])
            landmarks = values["landmarks"]
            landmarks.setCrs(values["crs"])
            bench_feature = [feature.geometry().asPoint() for feature in
                             benchmark.getFeatures()]
            start = QgsPoint(bench_feature[0].x(), bench_feature[0].y())
            land_points = [feature.geometry().asPoint() for feature in
                           landmarks.getFeatures()]
            feat_set = list()
            counter = 0
            for _ in land_points:
                new_feat = QgsFeature()
                new_feat.setGeometry(
                    QgsGeometry.fromPolyline([start,
                                              QgsPoint(land_points[
                                                           counter])]))
                counter += 1
                feat_set.append(new_feat)
            layer = self.new_vector_layer(geometry='Linestring',
                                          name='guides',
                                          memory='memory',
                                          fields={"Data": QVariant.String},
                                          f_list=feat_set)
            layer = self.calc_landmarks_fields(layer, values)
            layer.setCrs(values["crs"])
            layer.commitChanges()
            QgsProject.instance().addMapLayer(layer)

    def calc_landmarks_fields(self,
                              layer: QgsVectorLayer,
                              values: Dict[str, any]
                              ) -> QgsVectorLayer:
        """
        This method calculates landmarks fields az and len and write data
        to "Data" field.

        :param layer: input layer
        :type layer: QgsVectorLayer
        :param values: dict of interface data
        :type values: Dict[str, any]
        :rtype: QgsVectorLayer
        """

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.
                             globalProjectLayerScopes(layer))
        counter = 0
        with edit(layer):
            for feature in layer.getFeatures():

                geom = feature.geometry()
                context.setFeature(feature)
                direction = self.decimal_to_dms(
                    self.direction.evaluate(context))
                result = f"{values['names'][counter]} " \
                         f"{self.land_str[values['lang']][1]}. " \
                         f"{direction} " \
                         f"{round(geom.length(), 2)}" \
                         f"{self.land_str[values['lang']][0]}"
                self.landmarks_data["Nm"].append(values['names'][counter])
                self.landmarks_data["Az"].append(direction)
                self.landmarks_data["Len"].append(round(geom.length(), 2))
                feature["Data"] = result
                layer.updateFeature(feature)
                counter += 1
        return layer

    @error_handler("Coordinates handler")
    def coord_handler(self, values: Dict[str, any]) -> None:
        """
        This method handles coordinates data and write it in output field
        self.coordinate_data. It calculates coordinates in selected crs and in
        4326.

        :param values: dict of interface data
        :type values: Dict[str, any]
        """

        if values.get("t_points"):
            instance = QgsProject.instance()
            points = values["t_points"]
            points.setCrs(values["crs"])
            points.updateExtents()
            points.commitChanges()
            wgs = QgsCoordinateReferenceSystem(4326)
            own = QgsCoordinateReferenceSystem(points.crs())
            p_feature = [feature.geometry() for feature in
                         points.getFeatures()]
            count = 0
            tr = QgsCoordinateTransform(own, wgs, instance)
            for feature in p_feature:
                feature.transform(tr)
                feature = feature.asPoint()
                self.coord_data["Nm"].append(values["order"][count])
                self.coord_data["X"].append(
                    self.decimal_to_dms(feature.y()))
                self.coord_data["Y"].append(
                    self.decimal_to_dms(feature.x()))
                count += 1
            tr = QgsCoordinateTransform(wgs, values["crs"], instance)
            for feature in p_feature:
                feature.transform(tr)
                feature = feature.asPoint()
                self.coord_data["X1"].append(round(feature.y(), 3))
                self.coord_data["Y1"].append(round(feature.x(), 3))

    def borders_handler(self, values: Dict[str, any]):
        """
        This method handles borders data and write it in output field
        self.borders_data. It calls borders_segments method with parts in the
        loop if user check this field, else without parts.

        :param values: dict of interface data
        :type values: Dict[str, any]
        """

        if len(values["parts"]):
            check = False
            for part in values["parts"]:
                check = self.borders_segments(values, part)
            return check
        print("I GET borders")
        return self.borders_segments(values)

    @error_handler("Borders handler")
    def borders_segments(self, values: Dict[str, any],
                         part: Union[bool, List[int]] = False) -> Union[bool,
                                                                        None]:
        """
        This method handles borders segments.

        :param values: dict of interface data
        :type values: Dict[str, any]
        :param part: part of boundary
        :type part: List[int]
        """

        if values.get("t_points") and values.get("order"):
            points = values["t_points"]
            points.setCrs(values["crs"])
            points.updateExtents()
            points.commitChanges()
            request = QgsFeatureRequest()
            order_name: str = values["order_name"]
            clause = QgsFeatureRequest.OrderByClause(order_name,
                                                     ascending=True)
            orderby = QgsFeatureRequest.OrderBy([clause])
            request.setOrderBy(orderby)
            p_features = [QgsPoint(feature.geometry().asPoint()) for
                          feature in points.getFeatures(request)]
            if not part:
                ran = [1, len(p_features) + 1]
                l_features = self.border_lines(ran, p_features, values)
            else:
                l_features = self.border_lines(part, p_features, values)
            lines = self.new_vector_layer(geometry='Linestring',
                                          name='border',
                                          memory='memory',
                                          fields={"Data": QVariant.String},
                                          f_list=l_features)
            lines.setCrs(values["crs"])
            lines.commitChanges()
            QgsProject.instance().addMapLayer(lines)
            print("I Handled borders")
        else:
            return False

    def border_lines(self, ran: List[int],
                     feats: List[QgsPoint],
                     values: Dict[str, any]) -> List[QgsFeature]:
        """
        This method create's polylines of border and write it in
        output field self.borders_data.

        :param ran: range of points
        :type ran: List[int]
        :param values: dict of interface data
        :type values: Dict[str, any]
        :param feats: border turning points
        :type feats: List[QgsPoint]
        :rtype: List[QgsFeature]
        """

        l_features = list()
        feats = feats[ran[0] - 1: ran[1]]
        first = feats[0]
        count = 0
        for feature in feats:
            if count < len(feats) - 1:
                start = QgsPoint(feature.x(), feature.y())
                end = QgsPoint(feats[count + 1].x(),
                               feats[count + 1].y(), )
                self.bound_data["From"].append(ran[0] + count)
                self.bound_data["To"].append(ran[0] + count + 1)
            else:
                start = QgsPoint(feats[count].x(),
                                 feats[count].y(), )
                end = first
                self.bound_data["From"].append(ran[0] + count)
                self.bound_data["To"].append(ran[0])
            azimuth = self.cart_to_pol(start.azimuth(end))
            length = round(start.distance(end.x(), end.y()), 2)
            self.bound_data["Az"].append(
                self.decimal_to_dms(azimuth))
            self.bound_data["Len"].append(length)
            new_feat = QgsFeature()
            new_feat.setGeometry(
                QgsGeometry.fromPolyline([start, end]))
            if values.get("surface") and len(values["surface"]):
                surface = self.check_if_crosses(new_feat, values)
            else:
                surface = ""
            desc = self.lang_select(values)
            self.bound_data["Desc"].append(
                desc.format(length, self.az_to_str(azimuth, values), surface))
            count += 1
            l_features.append(new_feat)
        print("Im Created lines")
        return l_features

    def check_if_crosses(self, line: QgsFeature,
                         values: Dict[str, any]) -> str:
        """
        This method checks if line crosses layers ("surface" in interface).
        It returns list of layers.

        :param line: input line
        :type line: QgsFeature
        :param values: dict of interface data
        :type values: Dict[str, any]
        :rtype: str
        """

        feat_list = list()
        line = line.geometry()
        if values.get("surface"):
            surface = values["surface"]
            for layer in surface:
                own = layer[0].crs()
                self.update_crs(layer[0], values["crs"])
                for feat in layer[0].getFeatures():
                    feat_list.append((feat.geometry(), layer[0].name()))
                self.update_crs(layer[0], own)
            layers = list()
            for feat in feat_list:
                if line.crosses(feat[0]) or line.intersects(feat[0]):
                    layers.append(feat[1])
            return ", ".join(layers)

    def lang_select(self, values: Dict) -> str:
        """
        This method returns text in language (selects in interface).

        :param values: dict of interface data
        :type values: Dict[str, any]
        :rtype: str
        """

        if values["lang"] is "Deutsch":
            return self.de
        elif values["lang"] is "English":
            return self.eng
        return self.ru

    @staticmethod
    def update_crs(layer: QgsVectorLayer, crs: QgsCoordinateTransform) -> None:
        """
        This method changes layer crs.

        :param layer: layer
        :type layer: QgsVectorLayer
        :param crs: crs
        :type crs: QgsCoordinateTransform
        """

        layer.setCrs(crs)
        layer.updateExtents()
        layer.commitChanges()

    @staticmethod
    def decimal_to_dms(deg: float) -> str:
        """
        This method transforms decimal to deg-min-sec format.

        :param deg: input decimal
        :type deg: float
        :rtype: str
        """

        integer = int(deg)
        minutes = int((deg - integer) * 60)
        seconds = round((((deg - integer)*60) - minutes) * 60, 3)
        return f"{integer}°{minutes}\'{seconds}\'\'"

    @staticmethod
    def cart_to_pol(angle: float) -> float:
        """
        This method transforms standard Qgis azimuth to north based.

        :param angle: input angle
        :type angle: float
        :rtype: float
        """

        if angle < 0.0:
            return angle + 360
        return angle

    @staticmethod
    def az_to_str(az: float, values: Dict) -> str:
        """
        This method transforms azimuth to text version.

        :param az: input angle
        :type az: float
        :param values: dict of interface data
        :type values: Dict[str, any]
        :rtype: str
        """

        lang = values["lang"]
        if az <= 11.25 or az >= 348.75:
            return "N" if lang is "English" or lang is "Deutsch" else "C"
        elif 11.25 <= az <= 33.75:
            return "NNE" if lang is "English" or lang is "Deutsch" else "ССВ"
        elif 33.75 <= az <= 56.25:
            return "NE" if lang is "English" or lang is "Deutsch" else "СВ"
        elif 56.25 <= az <= 78.75:
            return "EEN" if lang is "English" or lang is "Deutsch" else "ВВС"
        elif 78.75 <= az <= 101.25:
            return "E" if lang is "English" or lang is "Deutsch" else "В"
        elif 101.25 <= az <= 123.75:
            return "EES" if lang is "English" or lang is "Deutsch" else "ВВЮ"
        elif 123.75 <= az <= 146.25:
            return "SE" if lang is "English" or lang is "Deutsch" else "ЮВ"
        elif 146.25 <= az <= 168.75:
            return "SSE" if lang is "English" or lang is "Deutsch" else "ЮЮВ"
        elif 168.75 <= az <= 191.25:
            return "S" if lang is "English" or lang is "Deutsch" else "Ю"
        elif 191.25 <= az <= 213.75:
            return "SSW" if lang is "English" or lang is "Deutsch" else "ЮЮЗ"
        elif 213.75 <= az <= 236.25:
            return "SW" if lang is "English" or lang is "Deutsch" else "ЮЗ"
        elif 236.25 <= az <= 258.75:
            return "WWS" if lang is "English" or lang is "Deutsch" else "ЗЗЮ"
        elif 258.75 <= az <= 281.25:
            return "W" if lang is "English" or lang is "Deutsch" else "З"
        elif 281.25 <= az <= 303.75:
            return "WWN" if lang is "English" or lang is "Deutsch" else "ЗЗC"
        elif 303.75 <= az <= 326.25:
            return "WN" if lang is "English" or lang is "Deutsch" else "CЗ"
        elif 326.25 <= az <= 348.75:
            return "NNW" if lang is "English" or lang is "Deutsch" else "CCЗ"

    @staticmethod
    def new_vector_layer(geometry: str = "Linestring",
                         name: str = "NewVectorLayer",
                         memory: str = "memory",
                         fields=None,
                         f_list: List = None) -> QgsVectorLayer:
        """
        This method creates a new vector layer

        :param geometry: geometry type
        :type geometry: str
        :param name: new layer's name,
        :type name: str
        :param memory: layer's memory,
        :type memory: str
        :param fields: dict of fields,
        :type fields: Dict
        :param f_list: list of features
        :type f_list:: List[QgsFeature]
        :rtype: QgsVectorLayer
        """

        if fields is None:
            fields = dict()
        layer = QgsVectorLayer(geometry, name, memory)
        layer_provider = layer.dataProvider()
        for key in fields.keys():
            layer_provider.addAttributes([QgsField(key, fields[key])])
        layer_provider.addFeatures(f_list)
        layer.updateFields()
        layer.updateExtents()
        return layer


