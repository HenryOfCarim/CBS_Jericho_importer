# Clive Barker's Jericho .sm3 importer for Blender

 Port of a very old mesh (.sm3) importer to modern Blender.

 Original version was made by Glogow Poland Mariusz Szkaradek for Blender 2.4

Tested on Blender 3.6

![image](https://github.com/user-attachments/assets/d3fd80db-24d7-4fe1-a076-3df8a663be78)


Resources of the game are packed and compressed into .packed archives to unpack them you need to use N.Kindt's scripts for python
jericho_upack.py script will unpack in a folder next to your archive.

Example of usage in Windows CMD

`python3 jericho_unpack.py -file "D:\Games\Clive Barker's Jericho\Data00.packed"`

After unpacking, you need to decompress the extracted files
jericho_decompress.py will create a `_decompressed` folder with resources ready to be imported

`python3 jericho_decompress.py -path "D:\Clive Barker's Jericho\Data00"`

To install the addon, press Code>Download Zip
Run Blender>Edit>Preferences>Add-ons>Install, select the downloaded archive, and enable the addon
In the File>Import menu the .sm3 file option will appear
