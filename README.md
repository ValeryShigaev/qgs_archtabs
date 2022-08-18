# ArchTabs
<img src="http://cp82453.tmweb.ru/public_images/archtabs_image1.jpg">
QGIS plugin that allows you to get a description of the borders by turning points.
Additionally, the plugin allows you to get a description of the visible landmarks and the coordinates of the turning points.
The output is saved in the format of MS Excel.

## Get stated
 - It is recommended to run QGIS with admin rights
 - To work, you need three layers: landmarks, benchmark, turning points (point geometry)
 - It is recommended that all three of these elements be in the same coordinate system
### Basic data
| <img src="http://cp82453.tmweb.ru/public_images/archtabs_image2.jpg"> | - 1 Output file which data will be loaded<br/> - 2 Boundary turning points <br/> - 3 Turning points order field<br/> - 4 Landmarks<br/> - 5 Landmarks description field if it exists<br/> - 6 Benchmark from which there will be a description of distances and directions to landmarks<br/> - 7 Projection<br/> - 8 Output description language |
|-----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

If you do not specify a reference point and/or do not specify landmarks, only coordinate data and a description of the border will be saved
The output looks like:
- Landmarks</br>
<img src="http://cp82453.tmweb.ru/public_images/archtabs_image3.jpg"></br>
- Coordinates</br>
<img src="http://cp82453.tmweb.ru/public_images/archtabs_image4.jpg"></br>
- Border description</br>
<img src="http://cp82453.tmweb.ru/public_images/archtabs_image5.jpg"> 

### Additional data
| <img src="http://cp82453.tmweb.ru/public_images/archtabs_image6.jpg"> | - 1 Check this if your border consists of several parts. Then add ranges of points to the table<br/> - 2 Rewrite the table if an error was made <br/> - 3 Check this if you want the description to include the names of the geometries along which the border passes<br/>  |
|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
