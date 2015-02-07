import Image
import re
import math

class BFFormatter(object):
    """
    Formats brainfuck source code according to a given image in ASCII art style 
    by placing a character wherever the (normalized) luminosity of the image is 
    smaller than a threshold value and placing a whitespace otherwise.
    """
    bf_string = None

    def __init__(self, bf_string=None, bf_file=None, strip_comments=False):
        """
        :param bf_string: Brainfuck source code.
        :type bf_string: str
        :param bf_file: Brainfuck source filename.
        :type bf_file: str
        :param strip_comments: Strip comments, i.e. any characters but []<>+-.,
        :type strip_comments: bool
        """
        if bf_string is not None:
            self.bf_string = bf_string
        elif bf_file is not None:
            with open(bf_file, "r") as f:
                self.bf_string = f.read().replace('\n', '')
        else:
            raise ValueError("Either bf_string or bf_file have to be provided.")
        if strip_comments:
            self.bf_string = re.sub(r"[^\[^\]^<^>^\.^,^\+^-]", "", self.bf_string)

    def format(self, image_file, output_file, invert=False, ws_fraction=0.5):
        """Format brainfuck code according to the given image file.

        :param image_file: Filename of image to be used.
        :type image_file: str
        :param output_file: Output filename.
        :type output_file: str
        :param invert: Invert image.
        :type invert: bool
        :param ws_fraction: The fraction of whitespace present in the image. 
                            Controls the output resolution.
        :type ws_fraction: float
        """
        if ws_fraction >= 1 or ws_fraction < 0:
            raise ValueError("White space fraction must be a number from the interval [0, 1).")
        img = Image.open(image_file)
        n = len(self.bf_string)
        n_scaled = int(n//(1-ws_fraction))
        # resize image
        width = (n_scaled * img.size[0] / float(img.size[1]))**0.5
        height = n_scaled/width
        width = int(math.ceil(width))
        height = int(math.ceil(height))
        img = img.resize((width, height))
        # calculate luminance
        Y = [(0.2126*px[0]+0.7152*px[1]+0.0722*px[2])/255 for px in img.getdata()]
        output_str = ""
        if invert is True:
            inv = -1
        else:
            inv = 1
        c = 0
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                idx =y*width+x
                if c < n and inv*Y[idx] < inv*0.5:
                    output_str += self.bf_string[c]
                    c+=1
                else:
                    output_str += " "
            output_str += "\n"
        if c < n:
            output_str += self.bf_string[c:]
        with open(output_file, "w") as f:
            f.write(output_str)
        return output_str

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='BrainFuck ASCII Art Formatter.')
    parser.add_argument('bf_file', metavar='bf_file', type=str, nargs=1,
                        help='Brainfuck source code file to be formatted.')
    parser.add_argument('image_file', metavar='image_file', type=str, nargs=1,
                        help='Image file to be used as a template.')
    parser.add_argument('output_file', metavar='output_file', type=str, nargs=1,
                        help='Output file.')
    parser.add_argument('--sc', help='Strip comments, i.e. any characters but []<>+-.,', 
                        action="store_true")
    parser.add_argument('--inv', help='Invert image.', action="store_true")
    parser.add_argument('--frac', type=float, 
                        help='Fraction of white in the image. This controls the resolution of the resulting rendering. (default: 0.5)', 
                        default=0.5)
    args = parser.parse_args()
    bff = BFFormatter(bf_file=args.bf_file[0], strip_comments=args.sc)
    bff.format(args.image_file[0], args.output_file[0], invert=args.inv, 
                ws_fraction=args.frac)
    print "Output written to %s." % args.output_file[0]
