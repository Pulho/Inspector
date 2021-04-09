# Inspector
A PNG file inspector, capable of detecting faults and corrupted blocks

### About the script
The purpose behind the script is to be able to bring a complete analysis of images of the PNG format, as well as to try to detect errors in corrupted images.
For this script it is necessary Python3.

### How to use it

```
Usage:
        inspector [OPTIONS] [FILE]

Options:
        -ff, --fixfile:
                Try to fix file bytes (Recommended to backup the file before using it)

        -ft, --forcetype:
                Treats the file as PNG
```
Ps.: With the fixFile parameter it is recommended to make a copy of the file in question, as this parameter will possibly make changes to the bytes of the image.

### Exemple of output
Taking the same image as the basis for the following two outputs
* For the first case we will run the script without parameter. In the case of this image, it has the header bytes outside the default of a PNG, thus not normally recognized
  ```
  Magic bytes not recognized
  ```
* For the second case, we will run the script with the parameter _forceType_ (-_ft_), so this way, even if the image does not have the magic bytes recognized, it continues to be treated as a PNG
  ```
  Showing file Propriety:
  Chunks Order: ['IHDR', 'tEXt', 'pLTE', 'IDAT', 'IEND']
  Dimension: 0x0
  HEADER ERROR: Header not found at the begin bytes of the file. Instead:
          83 50 4e 47 0d 0a 0a 0a 00 00 00 0d
  IHDR ERROR: Width value is 0
  IHDR ERROR: Height value is 0
  IHDR ERROR: Not capable of finding file dimension
  Bit depth: 8
  Color Type: 3 (Each pixel is a palette index. a PLTE chunk must appear). Bit depth allowed value 1,2,4,8.
  IHDR WARNING: CRC calculation does not match with the chunk. Possible loss of data
  tEXt:
          Hello, I'm a comment within the image
  tEXt WARNING: CRC calculation does not match with the chunk. Possible loss of data
  pLTE WARNING: CRC calculation does not match with the chunk. Possible loss of data
  PLTE ERROR: PLTE chunk must appear (Color type = 3), but there's none.
  WARNING: Weird chunk found on PNG file, named as pLTE with 768 bytes of size
  ```
* For the third and last case, we will run the script with the parameters _forceType_ (-_ft_) along with _fixFile_ (-_ff_), so that this way, some minor corrections can be made to the image we are analyzing. In this scenario, the script will use the brute force function to try to guess the dimensions of the image, through the chunk CRC.
  ```
  Correcting image dimension, this may take a while. . .



  Showing file Propriety:
  Chunks Order: ['IHDR', 'tEXt', 'pLTE', 'IDAT', 'IEND']
  Dimension: 1024x578
  FIXFILE: Header fixed from
          83 50 4e 47 0d 0a 0a 0a 00 00 00 0d
                  to
          89 50 4e 47 0d 0a 1a 0a 00 00 00 0d

  IHDR ERROR: Width value is 0
  IHDR ERROR: Height value is 0
  IHDR FIX: Dimension fixed to 1024x578
  Bit depth: 8
  Color Type: 3 (Each pixel is a palette index. a PLTE chunk must appear). Bit depth allowed value 1,2,4,8.
  IHDR WARNING: CRC calculation does not match with the chunk. Possible loss of data
  tEXt:
          Hello, I'm a comment within the image
  tEXt WARNING: CRC calculation does not match with the chunk. Possible loss of data
  pLTE WARNING: CRC calculation does not match with the chunk. Possible loss of data
  PLTE ERROR: PLTE chunk must appear (Color type = 3), but there's none.
  WARNING: Weird chunk found on PNG file, named as pLTE with 768 bytes of size
  ```
  
  ### Upcoming
  From one of the expected updates, we have the optimization of the brute force function in order to achieve greater efficiency
  
  ### References
  * [PNG File structure](https://github.com/rcrs4/Tebas/blob/master/forense/png/pt-br.md) (This material is in Portuguese)
  * <https://www.w3.org/TR/PNG>
  
  Author: [Paulo Victor](https://github.com/Pulho)
