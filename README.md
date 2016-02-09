# bladdons
Blender Addons


## Point Cloud Loader

This addon loads point cloud data (created to process recorded kinect data).

This addon can also help you to generate 3D mesh from the point cloud, but it depends on the [Point Cloud Skinner by Hans.P.G.](http://sourceforge.net/projects/pointcloudskin/) to create the actual mesh.

For a way to record kinect data using processing and the file format that is used, take a look [over here](http://moullinex.tumblr.com/post/3180520798/catalina-music-video). Note that I tweaked the python script, so that it doesn't require all the ignored (0.0,0.0,0.0) points to be in the file, which in some situations can drastically reduce the file size.

To use it, enable the Point Cloud Loader section in the object panel and specify which files to get the data from. It will automatically load a frame of point cloud data when the frame changes inside blender.