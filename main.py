import csv
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re

TYPEWRITER = ImageFont.truetype("./fonts/typewriter.TTF", size=65)
TYPEWRITER2 = ImageFont.truetype("./fonts/typewriter.TTF", size=55)
MODERNLINE = ImageFont.truetype("./fonts/modernline.OTF", size=55)

DEBUG = False
SPACING = 10

import re

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        u"\U0001F700-\U0001F77F"  # Alchemical Symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"  # Enclosed characters
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


def getEmojiMask(font: ImageFont, emoji: str, size: tuple[int, int]) -> Image:
    """ Makes an image with an emoji using AppleColorEmoji.ttf, this can then be pasted onto the image to show emojis
    
    Parameter:
    (ImageFont)font: The font with the emojis (AppleColorEmoji.ttf); Passed in so font is only loaded once
    (str)emoji: The unicoded emoji
    (tuple[int, int])size: The size of the mask
    
    Returns:
    (Image): A transparent image with the emoji
    
    """

    mask = Image.new("RGBA", (160, 160), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)
    draw.text((0, 0), emoji, font=font, embedded_color=True)
    mask = mask.resize(size)

    return mask

def getDimensions(draw: ImageDraw, text: str, font: ImageFont) -> tuple[int, int]:
    """ Gets the size of text using the font
    
    Parameters:
    (ImageDraw): The draw object of the image
    (str)text: The text you are getting the size of
    (ImageFont)font: The font being used in drawing the text
    
    Returns:
    (tuple[int, int]): The width and height of the text
    
    """
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=font)
    return (right-left), (bottom-top)


def createNotecard(response: str) -> Image.Image:
    img = Image.new(mode="RGB", size=(3400//2, 4400//4), color=(255, 255, 255))
    heart = Image.open("images/heart.png", mode="r")
    heart = heart.resize((125, 125))
    img.paste(heart, ((3400//2-heart.size[0])//2, 80))

    draw = ImageDraw.Draw(img)

    nresponse = "\n".join(["\n".join(textwrap.wrap(subtext, width=45)) for subtext in response.split("\n")]) # Response is separated by newlines so it doesn't run off the screen
    modifiedresponse = remove_emojis(nresponse)
    _, rheight = getDimensions(draw, modifiedresponse, TYPEWRITER)
    for index, line in enumerate(modifiedresponse.split("\n")):
        width, _ = getDimensions(draw, line, TYPEWRITER)
        
        draw.text((3400//4-width//2, (4400//4-rheight)//2+SPACING*index), "\n"*index+line, fill=(0, 0, 0), font=TYPEWRITER)

    MARGIN = 100
    MARGIN2 = 150

    # width, _ = getDimensions(draw, "Thank you", MODERNLINE) # Width of Thank you message is 240
    draw.text((3400//4-240//2, 4400//4-MARGIN-MARGIN2), "Thank you", fill=(0, 0, 0), font=MODERNLINE)

    width, _ = getDimensions(draw, "@wrhs_smileproject", TYPEWRITER2) # Width of @wrhs_smileproject message is 624
    draw.text((3400//4-width//2, 4400//4-MARGIN), "@wrhs_smileproject", fill=(0, 0, 0), font=TYPEWRITER2)


    return img


def combineNotecards(notecards: list[str]) -> Image.Image:
    img = Image.new(mode="RGB", size=(3400, 4400), color=(255, 255, 255))
    for index, notecard in enumerate(notecards):
        img.paste(notecard, (((index // 4 + index) % 2)*3400//2, (index % 4)*4400//4))
    return img

with open('data-teachers_2025.csv', encoding='utf-8-sig', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    n = 0
    notecards = []
    for row in reader:
        notecard = createNotecard(row['Response'])
        if (DEBUG):
            notecard.show()
            input()
            continue
        notecards.append(notecard)
        if (len(notecards) == 8):
            cards = combineNotecards(notecards)
            cards.save("images/out/notecards_%s.png" % n)
            print(n)

            notecards = []
            n += 1
    
    if (notecards):
        cards = combineNotecards(notecards)
        cards.save("images/out/notecards_%s.png" % n)
        print(n)
