from tkinter import *
from tkinter import ttk
from tkinter import colorchooser

import resolution as res

#create verticall scroll frames

class ScrollingFrame:

   def __init__(self, master, root, width, height, **kwargs):

      self.master = master
      self.root = root

      self.mainFrame_width = res.sx(width)
      self.mainFrame_height = res.sy(height)

      self.bgColour = '#f0f0f0' if 'bg' not in kwargs else kwargs['bg']
      self.scrollingIncrement = 1 if 'increments' not in kwargs else (kwargs['increments'] if kwargs['increments'] >= 1 else 1)

      self.scrollbar_ySpan = res.sy((self.mainFrame_height / 2) - 30)

      #mainframe contains both the viewing frame and the scrollbar frame
      self.mainFrame = Frame(self.root, width = self.mainFrame_width, height = self.mainFrame_height, bg = self.bgColour)

      self.viewFrame = Frame(self.mainFrame, width = self.mainFrame_width - res.sx(20), height = self.mainFrame_height, bg = self.bgColour)

      self.scrollFrame = Frame(self.mainFrame, width = res.sx(20), height = self.mainFrame_height, bg = self.bgColour)

      #viewing canvas will move in accordance to the scrollbar
      self.viewingCanvas = Canvas(self.viewFrame, width = self.mainFrame_width, height = self.mainFrame_height, bg = self.bgColour,
                                  bd = 0, highlightthickness = 0, relief = RIDGE)

      # scrollbar will control the vercial movement of the viewingCanvas
      self.scrollbar = ttk.Scrollbar(self.scrollFrame, orient = VERTICAL, command = self.viewingCanvas.yview)
      self.scrollbar.grid(row = 0, column = 0, ipady = self.scrollbar_ySpan, sticky = N)

      #canvas frame contains all the information that will be scrolled vertically while the user interacts with the scrollbar
      self.canvasFrame = Frame(self.viewingCanvas, bg = self.bgColour)

      #configuration steps
      self.viewingCanvas.configure(yscrollcommand = self.scrollbar.set)
      self.viewingCanvas.bind('<Configure>', lambda e: self.viewingCanvas.configure(scrollregion = self.viewingCanvas.bbox('all')))
      self.viewingCanvas.create_window((0, 0), window = self.canvasFrame, anchor = 'nw')

   # def create_load_button(self, env, text, font, width):
      
   #    self.load_button = Button(env, text = text, font = font, width = width, command = self.load())

   # def create_unload_button(self, env):
      
   #    self.load_button = Button(env, text = text, font = font, width = width, command = self.load())

   def load(self, **kwargs):

      self.mainFrame.grid_propagate(0)
      self.viewFrame.grid_propagate(0)
      self.scrollFrame.grid_propagate(0)
      self.viewingCanvas.grid_propagate(0)

      self.viewFrame.grid(row = 0, column = 0)
      self.scrollFrame.grid(row = 0, column = 1)
      self.viewingCanvas.grid(row = 0, column = 0)

      self.mainFrame.grid(row = kwargs['row'] if 'row' in kwargs else 0, 
                          column = kwargs['column'] if 'column' in kwargs else 0, 
                          padx = kwargs['padx'] if 'padx' in kwargs else 0,
                          pady = kwargs['pady'] if 'pady' in kwargs else 0,
                          sticky = kwargs['sticky'] if 'sticky' in kwargs else None)

      self.master.bind('<MouseWheel>', self.mousewheelScrolling)

      self.master.update_idletasks()

   def unload(self, **kwargs):

      self.mainFrame.grid_forget()
      self.viewFrame.grid_forget()
      self.scrollFrame.grid_forget()
      self.viewingCanvas.grid_forget()

      self.viewingCanvas.config(width = self.mainFrame_width - 20)

      self.master.unbind('<MouseWheel>')

   def mousewheelScrolling(self, event, *args):

      self.viewingCanvas.yview_scroll(int(-self.scrollingIncrement * (event.delta/120)), "units")

   def test_buttons(self, amount):

      for num in range(amount + 1):

         self.button = Button(self.canvasFrame, text = f'button {num}')
         self.button.grid(row = num, column = 0, padx = res.rx(370), pady = res.ry(15))

   def resizeScrollWindow(self):
      self.master.update_idletasks()
      self.viewingCanvas.configure(scrollregion = self.viewingCanvas.bbox('all'))

   def flatten(self, amount):

      self.viewingCanvas.config(height = self.mainFrame_height - amount)
      self.viewingCanvas.configure(scrollregion = self.viewingCanvas.bbox('all'))
      self.scrollbar.grid_configure(ipady = self.scrollbar_ySpan - int(amount / 2))

   def heighten(self, amount):

      self.scrollbar.grid_configure(ipady = self.scrollbar_ySpan)
      self.viewingCanvas.config(height = self.mainFrame_height)
      self.viewingCanvas.configure(scrollregion = self.viewingCanvas.bbox('all'))

def encode(data): #accepts a dictionary, converts keys / values of dict into a storage format and returns an encode string
   dataText = ''
   for kana in data:

      kanaText = kana
      engText = '/'.join(data[kana])

      dataText += f'{kanaText}:{engText}|'

   return dataText

   #かんが:think/consider/thinking/thoughts|かんがえ:thinking/thoughts/imagination/opinion|かんがえる:think/think about/consider/reflect| 

   #DATA FORMAT:

   # ( : ) - divides hiragana characters and english words. --eg-> かんが:think
   # ( / ) - divides multiple english words., will not exist if there is only one english word. --eg-> think/consider/thinking
   # ( | ) - divides 2 groups of related hiragana characters and english words. --eg-> #かんが:think|かんがえ:thinking/thoughts
   # ( > and < ) - used to highlight specific hiragana characters to display in different colours. --eg-> かんが#00ffff>え< (OMIT FOR NOW)

def decode(code, **kwargs):

   # if 'default' not in kwargs:
   #    defaultColour = '#000000'
   # else:
   #    defaultColour = kwargs['default']

   #separating the string based on its '|' divider
   stringList = code.split('|')
   stringList.remove(stringList[-1])

   #create a dictionary of kana keys and english values (seprataed by ':')
   slashDict = {string[:string.index(':')]: string[string.index(':') + 1:] for string in stringList}

   #separate english words in a list (separated by '/')
   kanaDict = {kana: slashDict[kana].split('/') for kana in slashDict}

   return kanaDict

class Colourful_texts:

   def __init__(self, data, canvas, font, indent):

      print(data, canvas, font)

      self.canvas = canvas
      self.font = font
      self.indent = indent

      self.x = 0
      self.prev_x = 0
      y = int(self.canvas.winfo_reqheight() / 2)

      for num, RGB in enumerate(data, start = 1):

         text = data[RGB]
         hex_colour = f'#{RGB[0]:02x}{RGB[1]:02x}{RGB[2]:02x}'

         canvasText = self.canvas.create_text(self.x, y, text = text, fill = hex_colour, font = self.font)
         box1 = self.canvas.bbox(canvasText)
         tBox_radius = int((box1[2] - box1[0]) / 2)

         if num == 1: #initial text
            self.canvas.move(canvasText, tBox_radius + self.indent, 0)

         else: #all other texts

            self.canvas.move(canvasText, tBox_radius + self.prev_x - 2, 0) # '-2' is for optimization.

         box2 = self.canvas.bbox(canvasText)
         # textBorder = self.canvas.create_line(box2[0], box2[1], box2[2], box2[1], box2[2], box2[3], box2[0], box2[3], box2[0], box2[1])

         self.x = int((box2[0] + box2[2]) / 2)
         self.prev_x = tBox_radius

class tags_Window:

   def __init__(self, availableTags, **kwargs):

      self.btnFg = '#cbcbcb'
      self.mainBg = kwargs['bg'] if 'bg' in kwargs else '#000000'
      self.defaultOn = kwargs['default'] if 'default' in kwargs else []
      self.permTag = kwargs['permanent'] if 'permanent' in kwargs else None
      self.invoke = kwargs['invoke'] if 'invoke' in kwargs else None
      self.update = kwargs['update'] if 'update' in kwargs else None
      self.delete = kwargs['delete'] if 'delete' in kwargs else None

      self.tagsStored = availableTags

      self.newTagColour = '#ff0000'

      self.root = Toplevel(bg = self.mainBg)
      self.root.title('Tags chooser')
      self.root.geometry('460x700+0+50')

      self.showTagsWindow = Frame(self.root, bg = '#ffffff')
      self.showTagsWindow.pack(pady = 5)

      self.showTagsFrame = Frame(self.showTagsWindow, width = res.rx(401), height = res.ry(450), bg = '#131313')
      self.showTagsFrame.grid_propagate(0)
      self.showTagsFrame.grid(row = 0, column = 0, padx = res.rx(3), pady = res.ry(3))

      self.tagsDict = {}
      self.selectedTags = []

      #variable to check if there are no tags being shown on screen
      self.displayNone = False
      self.noTagsLabel = Label(self.showTagsFrame, text = 'No such tags \n exist.', font = ('arial', res.ry(30)), bg = '#131313', fg = '#4f4f4f')

      for num, tag in enumerate(availableTags):
         text, hexColour = tag[0], tag[1]
         self.tagsDict[text] = self.create_new_tag(text, hexColour)
         self.newTagPosition = self.display_tag(text, self.tagsDict[text], num)

      self.newTagsFrame = Frame(self.root, bg = '#1f2e1f')
      self.newTagButton = Button(
          self.newTagsFrame,
          text='New Tag',
          font=('arial', res.sy(18)),
          width=res.sx(8),
          bg='#004d00',
          fg=self.btnFg,
          state=DISABLED
      )
      self.tagColourButton = Button(
          self.newTagsFrame,
          width=res.sx(2),
          bg=self.newTagColour,
          command=self.load_colour_chooser
      )
      self.deleteTagButton = Button(
          self.newTagsFrame,
          text=u'\u274c',
          font=('arial', res.sy(10)),
          width=res.sx(2),
          bg=self.btnFg,
          fg='#6f0000',
          state=DISABLED
      )

      self.searchTagsLabel = Label(
          self.newTagsFrame,
          text='Search Tag(s):',
          font=('arial', res.sy(16)),
          bg='#1f2e1f',
          fg=self.btnFg
      )
      self.searchTracker = StringVar(name='serachTracker')
      self.searchTracker.trace_add('write', self.display_searched_tags)
      self.searchTagEntry = Entry(
          self.newTagsFrame,
          font=('arial', res.sy(22)),
          width=res.sx(10),
          textvariable=self.searchTracker
      )
      self.searchTagEntry.focus_set()

      self.textTracker = StringVar(name='textTracker')
      self.textTracker.trace_add('write', self.update_new_tag)
      self.newTagEntry = Entry(
          self.newTagsFrame,
          width=res.sx(10),
          font=('arial', res.sy(22)),
          textvariable=self.textTracker
      )

      self.newTagButton.grid(row=0, column=0, pady=res.sy(10), padx=res.sx(20))
      self.newTagEntry.grid(row=0, column=1)
      self.tagColourButton.grid(row=0, column=2, padx=res.sx(20))
      self.deleteTagButton.grid(row=1, column=2)
      self.searchTagsLabel.grid(row=1, column=0, pady=res.sy(10))
      self.searchTagEntry.grid(row=1, column=1)
      self.newTagsFrame.pack(pady=res.sy(5))

      self.returnFrame = Frame(self.root, bg='#2b1f2e')
      self.confirmButton = Button(
          self.returnFrame,
          text='Confirm',
          font=('arial', res.sy(18)),
          bg='#2d2d53',
          fg=self.btnFg,
          width=res.sx(8),
          command=lambda: self.exit('confirm')
      )
      self.cancelButton = Button(
          self.returnFrame,
          text='Cancel',
          font=('arial', res.sy(18)),
          bg='#532d2d',
          fg=self.btnFg,
          width=res.sx(8),
          command=lambda: self.exit('cancel')
      )

      self.confirmButton.grid(row=0, column=0, padx=res.sx(20), pady=res.sy(20))
      self.cancelButton.grid(row=0, column=1, padx=res.sx(20))

      self.returnFrame.pack()

      self.root.protocol('WM_DELETE_WINDOW', lambda: self.exit('cancel'))
      self.root.mainloop()

   def create_new_tag(self, text, hexColour):
         rgb = tuple([int(hexColour[1:][2*i:2*(i+1)], 16) for i in range(3)])
         inactiveSelect = f"#{int(rgb[0] / 4):02x}{int(rgb[1] / 4):02x}{int(rgb[2] / 4):02x}"

         window = Frame(self.showTagsFrame, bg = hexColour)
         frame = Frame(window, width = res.sx(88), height = res.sy(22))
         button = Checkbutton(frame, text = text, font = ('arial', res.sy(9 - (len(text) // 8))), bg = '#1f1f1f', fg = '#ffffff', anchor = W, width = res.sx(10), 
                              selectcolor = inactiveSelect, variable = StringVar(name = text))
         button.config(command = lambda text = text, colour = hexColour, button = button: self.select_tags(text, colour, button))

         return (hexColour, window, frame, button)

   def display_tag(self, tag, tagTuple, position):
      rgb = tuple([int(tagTuple[0][1:][2*i:2*(i+1)], 16) for i in range(3)])

      if tag in self.defaultOn:
         tagTuple[3].select()
         tagTuple[3].config(bg = f'#{int(rgb[0] / 2):02x}{int(rgb[1] / 2):02x}{int(rgb[2] / 2):02x}',
                       selectcolor = '#ffffff')
         self.selectedTags.append((tag, tagTuple[0])) 

      row = position // 4
      column = position % 4

      tagTuple[2].pack_propagate(0)
      tagTuple[2].pack(padx = res.sx(1), pady = res.sy(1))
      tagTuple[3].pack(fill = BOTH, expand = 1)
      tagTuple[1].grid(row = row, column = column, padx = res.sx(5), pady = res.sy(5))

      return len(self.tagsDict)

   def update_tags(self, text, hexColour):

      self.searchTagEntry.delete(0, END)

      if not (text in self.tagsDict): #new tag

         self.tagsDict[text] = self.create_new_tag(text, hexColour)
         self.tagsDict[text][3].select()

         row = self.newTagPosition // 4
         column = self.newTagPosition % 4

         self.tagsDict[text][2].pack_propagate(0)
         self.tagsDict[text][2].pack(ppadx = res.sx(1), pady = res.sy(1))
         self.tagsDict[text][3].pack(fill = BOTH, expand = 1)
         self.tagsDict[text][1].grid(row = row, column = column, padx = res.sx(5), pady = res.sy(5))

         # self.tagsDict[text] = (colour, window, frame, button)
         self.selectedTags.append((text, hexColour))
         self.tagsStored.append((text, hexColour))

         if self.update != None:
            self.update('new', text, hexColour)

      else:
         rgb = tuple([int(hexColour[1:][2*i:2*(i+1)], 16) for i in range(3)])
         self.tagsDict[text][1].config(bg = hexColour)
         self.tagsDict[text][3].config(selectcolor = f"#{int(rgb[0] / 4):02x}{int(rgb[1] / 4):02x}{int(rgb[2] / 4):02x}")

         for num, tag in enumerate(self.tagsStored):
            if text == tag[0] and self.update != None:
               self.tagsStored[num] = (text, hexColour)
               self.update('edit', text, hexColour)
               break

      self.newTagPosition = len(self.tagsDict)
      self.newTagEntry.delete(0, END)

   def load_colour_chooser(self, *args):

      self.colorChoice = colorchooser.askcolor(title = 'Choose tag colour', initialcolor = self.newTagColour)
      self.newTagColour = self.colorChoice[1]
      self.tagColourButton.config(bg = self.colorChoice[1])

   def update_new_tag(self, *args):
      text = self.textTracker.get()
      self.newTagButton.config(command = lambda: self.update_tags(text, self.newTagColour))

      if text != '':
         if text not in self.tagsDict:
            self.newTagButton.config(text = 'New Tag', state = NORMAL)
            self.deleteTagButton.config(state = DISABLED, command = None)

         else:
            self.newTagButton.config(text = 'Edit Tag')
            self.newTagColour = self.tagsDict[text][0]
            self.tagColourButton.config(bg = self.newTagColour)
            self.deleteTagButton.config(state = NORMAL, command = lambda: self.delete_tag(text))

      else:
          self.newTagButton.config(text = 'New Tag', state = DISABLED)
          self.deleteTagButton.config(state = DISABLED, command = None)

   def delete_tag(self, text):

      self.tagsDict[text][1].destroy()

      tagList = [tag for tag in self.tagsDict]
      startIndex = tagList.index(text)

      counter = startIndex
      for tag in tagList[startIndex + 1:]:

         row = counter // 3
         column = counter % 3
         self.tagsDict[tag][1].grid_configure(row = row, column = column)

         counter += 1

      del self.tagsDict[text]

      if self.delete != None:
         self.delete(text)

      self.newTagEntry.delete(0, END)

   def select_tags(self, tag, col, btn):

      rgb = tuple([int(col[1:][2*i:2*(i+1)], 16) for i in range(3)])
      pair = (tag, col)
      if not (pair in self.selectedTags):
         self.selectedTags.append(pair)
         btn.config(bg = f'#{int(rgb[0] / 2):02x}{int(rgb[1] / 2):02x}{int(rgb[2] / 2):02x}',
                    selectcolor = '#ffffff')

      else:
         self.selectedTags.remove(pair)
         btn.config(bg = '#1f1f1f',
                    selectcolor = f"#{int(rgb[0] / 4):02x}{int(rgb[1] / 4):02x}{int(rgb[2] / 4):02x}")

      self.searchTagEntry.delete(0, END)

   def display_searched_tags(self, *args):
      text = self.searchTagEntry.get()

      dispCounter = 0
      for tag in self.tagsDict:

         textExists = (text.lower() in tag.lower())

         row = dispCounter // 4
         column = dispCounter % 4

         if textExists and (self.tagsDict[tag][1].winfo_ismapped() == 1): #configure grid
            self.tagsDict[tag][1].grid_configure(row = row, column = column)
            dispCounter += 1

         elif (textExists and (self.tagsDict[tag][1].winfo_ismapped() == 0)) or (text == ''): #map
            self.tagsDict[tag][1].grid(row = row, column = column, padx = res.sx(5), pady = res.sy(5))
            dispCounter += 1

         elif not textExists and (self.tagsDict[tag][1].winfo_ismapped() == 1): #unmap
            self.tagsDict[tag][1].grid_forget()

         elif not textExists and (self.tagsDict[tag][1].winfo_ismapped() == 0): #do nothing
            pass  

      if (dispCounter == 0) and (not self.displayNone):
         self.displayNone = True
         self.noTagsLabel.grid(row = 0, column = 0, padx = 79, pady = 149)

      elif (dispCounter > 0) and self.displayNone:
         self.displayNone = False
         self.noTagsLabel.grid_forget()

   def exit(self, keyword):

      self.searchTracker.trace_remove('write', self.searchTracker.trace_vinfo()[0][1])
      self.textTracker.trace_remove('write', self.textTracker.trace_vinfo()[0][1])
      self.searchTagEntry.delete(0, END)
      self.newTagEntry.delete(0, END)

      if keyword == 'confirm':

         if self.invoke != None:
            self.invoke(self.selectedTags)

      elif keyword == 'cancel':
         pass

      self.root.destroy()
      del self
      
def open_tags_window(tags, **kwargs):

   tagsWindow = tags_Window(tags, **kwargs)


# test_data1 = {(0, 0, 0): 'be', (255, 0, 0): 'li', (0, 128, 0): 'e', (0, 0, 255): 've', (128, 128, 128): ' it!'}
# data_string = 'まる:circle|まる#0000ff>い<:circle/circular/sphere/spherical|ガン:fishball/meatball|'

# if __name__ == '__main__':

#    from tkinter import *

#    sample_data = {'一': {'hiragana': ['いち']}}

#    root = Tk()
#    root.title('testing window')
#    root.geometry('600x400')

#    aFrame = Frame(root, bg = '#00ffff', width = 400, height = 300)
#    aFrame.pack_propagate(0)
#    aFrame.pack()

#    aCanvas = Canvas(aFrame, width = 500, height = 200, bg = 'white')
#    aCanvas.grid(row = 0, column = 0)

#    result = Colourful_texts(test_data1, aCanvas, ('arial', 20), 20)

#    encoded_string = encode(sample_data)
#    decoded_data = decode(data_string)

#    root.mainloop()

# else:
#    print('loaded knowledge')

def get_char_pixels(fontSize):

   TL = Toplevel()
   label = Label(TL, font = ('arial', fontSize))

   chars = {}
   for char in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890,.'^() \n":

      label.config(text = char)
      width = label.winfo_reqwidth() - 6
      chars[char] = width if width > 0 else 1

   TL.destroy()
   return chars


if __name__ == '__main__':
   #TAGS LIST: (TAG, RGB)

   newTagWindow = tags_Window([('red', '#ff0000'), ('green', '#00ff00'), ('blue', '#0000ff'),
                               ('Polysemous', '#ff00ff'), ('yellow', '#ffff00'), ('cyan','#00ffff')], bg = 'gray')

def format_kana(kanas, width):
   #accepts a list of strings, converts it into a single string that occupies multiple lines, depending on how long each string in the list is
   maxChars = width
   maxLength = max([len(kana) for kana in kanas])
   kanasList = list(kanas)
   if maxLength <= maxChars:
      pass

   else:
      for num, kana in enumerate(kanasList):
         if len(kana) > maxChars:

            heightenedKana = ''
            for ind, char in enumerate(kana):

               if ((ind + 1) % maxChars) == 0 and ((ind + 1) != len(kana)):
                  heightenedKana += char + '\n'

               else:
                  heightenedKana += char

            kanasList[num] = heightenedKana

   return ''.join([kana + '\n' if num < len(kanasList) else kana for (num, kana) in enumerate(kanasList, start = 1)])


def format_english(engs, pixels, maxWidth):
   engText = ''
   for num, subEngs in enumerate(engs, start = 1):

      newEng = (', '.join(subEngs) + ('\n' if num != len(engs) else ''))
      lineLength = sum([pixels[eng] for eng in newEng]) + 6

      if lineLength > maxWidth:

         text = ''
         countLength = 0
         commaIndex = 0
         maximum = maxWidth
         for num, char in enumerate(newEng, start = 1):

            text += char

            if char == ',':
               commaIndex = num

            if countLength > maximum:
               engText += text[:commaIndex] + '\n'
               text = text[commaIndex + 1:]
               commaIndex = 0
               countLength = sum([pixels[char] for char in text])
               maximum = maxWidth - countLength

            countLength += pixels[char]

         engText += text

      else:
         engText += newEng

   return engText