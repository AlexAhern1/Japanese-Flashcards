#the new config file for kanji flashcards.
#all data storage and data manipulation shall be handled by this python script.

import os
import sqlite3
import datetime

from utilities import encode #, decode
import users
import sys
from pathlib import Path

#database file name

parentPath = Path(sys._MEIPASS) if getattr(sys, "frozen", False) is True else Path(__file__).resolve().parent.parent

databaseFolder = parentPath / "data"

kanjiFile = databaseFolder / 'kanji_new_database.db' #(kanji text, JandE text, grade text, jlpt text, tags text, DandT text)
kanaFile = databaseFolder / 'kana_database.db' #(kana text, english text, kanji text)
tagsFile = databaseFolder / 'tags_database.db' #(kana text, english text)

def getData():
   #obtains all information about kanji stored in .db file
   with sqlite3.connect(kanjiFile) as conn:
      c = conn.cursor()
      c.execute('SELECT * FROM main_dict')
      data_list = [list(data) for data in c.fetchall()] #IMPORTANT LIST
      kanji_list = [data[0] for data in data_list]
      size = len(data_list)

   with sqlite3.connect(kanaFile) as conn2:
      c = conn2.cursor()
      c.execute('SELECT * FROM hiragana')
      hiragana_list = list(c.fetchall())
      c.execute('SELECT * FROM katakana')
      katakana_list = list(c.fetchall())

   with sqlite3.connect(tagsFile) as conn3:
     c = conn3.cursor()
     c.execute('SELECT * FROM all_tags')
     tags_list = [list(tag) for tag in c.fetchall()]

   return (data_list, kanji_list, size, tags_list, hiragana_list, katakana_list)

def verify_username(inputName):
   #checks if the input username is part of the registered users
   for file in os.listdir('users'):
      with open(f"users/{file}", 'r') as profile:
         if inputName == profile.readline()[6:].strip():
            return True
            
   return False

def get_user_profile():
   #nub
   return 'nub'

def overwrite_default_user(currentDefaultUser, newDefaultUser):
   #changes the default user from current to new.
   for num, user in enumerate((currentDefaultUser, newDefaultUser)):
   #num will always be 0 or 1, which correlates to the user not being default, or being default, respectively.
      with open(f"users/{user}.txt", 'r') as readProfile:
         overwrittenDefault = [line if ind != 1 else f"DEFAULT: {num}\n" for (ind, line) in enumerate(readProfile)]

      with open(f"users/{user}.txt", 'w') as writeProfile:
         for line in overwrittenDefault:
            writeProfile.write(line)

def get_user_settings(*args):
   #obtains the user settings from a specified user.
   singleVariableDataKeys = ('time', 'lives', 'recover', 'language', 'repetition', 'gradelogic', 'jlptlogic', 'lengthlogic', 'tagslogic')
   #tuple containing the data keys that will only ever have one element. data under this category need not be appended to a list.
   for user in os.listdir(users.usersFile):
      with open(f"{users.usersFile}/{user}", 'r') as profile:
         defaultName = profile.readline().strip()
         if ((profile.readline().strip()[-1] == '1') if (args == ()) else (args[0] == defaultName[6:])):
         #if args is an empty tuple, obtain default user settings.
         #however if an input user is in args, obtain input user settings.
            settings = extract_user_settings(profile)

   return settings

def extract_user_settings(profile):
   #organises data into it's category and values.
   presetCount = 0
   presets = {}
   default = False
   for text in profile:

      info = text.strip()
      if info == '':
         pass
      else:
         category = info[:info.index(':')]
         data = info[info.index(':') + 1:]
         default = (info[-1] == '*')

      if (presetCount > 0) and not ('preset_' in info):
         presets[_preset_][category] = format_settings_data(category, data)

      elif ('preset_' in info):
         presetCount += 1
         _preset_ = data.rstrip('*') if default else data
         presets[_preset_] = {'default': default}

   return presets

def format_settings_data(category, data):
   #manages and formats how the user settings will be stored
   singleVariableDataKeys = ('time', 'lives', 'recover', 'language', 'repetition', 'gradelogic', 'jlptlogic', 'lengthlogic', 'tagslogic')
   if category in singleVariableDataKeys:
      return data

   elif data != 'none':
      return data.split(',')

   return []

def get_default_settings(allPresets):
   #gets the default preset of a user from all it's presets
   for preset in allPresets:
      if allPresets[preset]['default']:
         return allPresets[preset]

   #return blankPreset <- CREATE ONE

def set_default_preset(*args):
   #changes the default preset of a logged in user from current to new
   user, currentDefault, newDefault = args[0], args[1], args[2]
   overwrittenDefault = []
   with open(f"users/{user}.txt", 'r') as readProfile:
      for line in readProfile:
         if (currentDefault in line) and ('preset_' in line):
            overwrittenDefault.append(line[:-2] + '\n')

         elif (newDefault in line) and ('preset_' in line):
            overwrittenDefault.append(line[:-1] + '*\n')

         else:
            overwrittenDefault.append(line)

   with open(f"users/{user}.txt", 'w') as writeProfile:
      for line in overwrittenDefault:
         writeProfile.write(line)

def overwrite_preset_values(*args):
   #given a selected preset, overwrites all it's values with new changes made.
   user, presetName, presetValues = args[0], args[1], args[2]
   overwrittenDefault = []
   with open(f"users/{user}.txt", 'r') as readProfile:
      updatePreset = False
      for line in readProfile:
         info = line.strip()
         if 'preset_' in info and (info[info.index(':') + 1:-1] if ('*' in info) else info[info.index(':') + 1:]) == presetName:
            updatePreset = True
         
         elif info == '':
            updatePreset = False

         elif updatePreset:
            key = info[:info.index(':')]
            line = f"{key}:{presetValues[key]}\n"

         overwrittenDefault.append(line)

   with open(f"users/{user}.txt", 'w') as writeProfile:
      for line in overwrittenDefault:
         writeProfile.write(line)

def append_new_preset(*args):
   #saves a new preset in the user's text file.
   user, presetName, presetValues, presetNum = args[0], args[1], args[2], args[3] + 1
   with open(f"users/{user}.txt", 'a') as appendProfile:
      appendProfile.write('\n')
      appendProfile.write(f"preset_{presetNum}:{presetName}\n")
      for key in presetValues:
         appendProfile.write(f"{key}:{presetValues[key]}\n")


#tags db manipulation
def update_tags_database(type_, tag, rgb):

  with sqlite3.connect(tagsFile) as conn:
    c = conn.cursor()

    if type_ == 'new':
      c.execute('INSERT INTO all_tags VALUES (:tag, :rgb)', {'tag': tag, 'rgb': rgb})
      print('added new tag')

    elif type_ == 'edit':
      c.execute("UPDATE all_tags SET rgb = '{}' WHERE tag = '{}'".format(rgb, tag))
      print('updated tag')

def remove_tag_from_database(tag):
  with sqlite3.connect(tagsFile) as conn:
    c = conn.cursor()
    c.execute(f"DELETE FROM all_tags WHERE tag = '{tag}'")


def manual_add_tag(tag, colour):
  with sqlite3.connect(tagsFile) as conn:
    c = conn.cursor()
    c.execute('INSERT INTO all_tags VALUES (:tag, :rgb)', {'tag': tag, 'rgb': colour})

def replace_tag(current, new):

  with sqlite3.connect(kanjiFile) as conn:
    c = conn.cursor()

    c.execute('SELECT kanji, tags from main_dict')

    x = c.fetchall()

    for i in x:

      if current in i[1]:

        l1 = i[1].split(',')
        l1[l1.index(current)] = new
        s1 = ','.join(l1)

        print(i[0], s1)

        c.execute("UPDATE main_dict SET tags = '{}' WHERE kanji = '{}'".format(s1, i[0]))


def add_to_database(kanji, wordsDict, grade, jlpt, tags):

  timeNow = str(datetime.datetime.today())
  timeAdded = timeNow.rstrip(timeNow[::-1][:timeNow[::-1].index('.')][::-1]).rstrip('.')

  wordsString = encode(wordsDict)
  
  with sqlite3.connect(kanjiFile) as conn:
    c = conn.cursor()
    c.execute('INSERT INTO main_dict VALUES (:kanji, :JandE, :grade, :jlpt, :tags, :DandT)',
              {'kanji': kanji,
              'JandE': wordsString,
              'grade': grade,
              'jlpt': jlpt,
              'tags': tags,
              'DandT': timeAdded
              } )

    print('added kanji')

    return [kanji, wordsString, grade, jlpt, tags, timeAdded]

def remove_from_database(kanji):

   with sqlite3.connect(kanjiFile) as conn:
      c = conn.cursor()

      c.execute("DELETE from main_dict WHERE kanji = '{}'".format(kanji))
      c.execute('SELECT * FROM main_dict')

      data_list = [list(data) for data in c.fetchall()] #IMPORTANT LIST
      kanji_list = [data[0] for data in data_list]
      size = len(data_list)

   print(f'deleted {kanji}')

   return (data_list, kanji_list, size)

def edit_data(kanji, words, grade, jlpt, tags):
   dataList = (words, grade, jlpt, tags)
   with sqlite3.connect(kanjiFile) as conn:
      c = conn.cursor()
      for column, update in zip(('JandE', 'grade', 'jlpt', 'tags', 'pageHeight'), dataList):
         if type(update) == str and "'" in update:
            c.execute('UPDATE main_dict SET {} = "{}" WHERE kanji = "{}"'.format(column, update, kanji))

         elif type(update) == str and not ("'" in update):
            c.execute("UPDATE main_dict SET {} = '{}' WHERE kanji = '{}'".format(column, update, kanji))

         else:
            c.execute("UPDATE main_dict SET {} = {} WHERE kanji = '{}'".format(column, update, kanji))

   print('edited', kanji)


def add_new_hiragana(newhiragana, newmeanings, newkanji):
   with sqlite3.connect(kanaFile) as conn:
      c = conn.cursor()
      c.execute('INSERT INTO hiragana VALUES (:kana, :english, :kanji)', {'kana': newhiragana, 'english': newmeanings, 'kanji': newkanji})

def remove_hiragana(hiragana):
   with sqlite3.connect(kanaFile) as conn:
      c = conn.cursor()
      c.execute("DELETE from hiragana WHERE kana = '{}'".format(hiragana))


def add_new_katakana(newkatakana, newmeanings):
   with sqlite3.connect(kanaFile) as conn:
      c = conn.cursor()
      c.execute('INSERT INTO katakana VALUES (:kana, :english)', {'kana': newkatakana, 'english': newmeanings})


def remove_katakana(katakana):
   with sqlite3.connect(kanaFile) as conn:
      c = conn.cursor()
      c.execute("DELETE from katakana WHERE kana = '{}'".format(katakana))

if __name__ == '__main__':
  pass


else:
   pass

#----------MAY OR MAY NOT BE OBSOLETE FUNCTIONS----------#

# def set_default_values(data, user):
#    #set the 
#     textList = [f'{cat}:{data[cat]}' for cat in data]
#     for standardText in [f'NAME: {user}', 'DEFAULT: 1', 'DEFAULT GAME SETTINGS:', ''][::-1]:
#         textList.insert(0, standardText)
#     with open(f"users/{user}.txt", 'w') as writing:
#         for text in textList:
#             writing.write(text + '\n')
#     print('set as default.')

#     return True