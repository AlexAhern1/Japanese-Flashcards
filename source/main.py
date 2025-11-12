from tkinter import *

#custom modules
from utilities import *
import users
from translator import *

import config as cfg
import client
import library_editor
import game
import resolution as res

root = Tk()
res.SetScreenResolution(root.winfo_screenwidth(), root.winfo_screenheight())

xScale = res.GetScaledWidth()
yScale = res.GetScaledHeight()

width = 1440
height = 900

windowWidth = res.sx(width)
windowHeight = res.sy(height)

root.title('Japanese Flashcards') 
root.geometry(f'{windowWidth}x{windowHeight}+{(res.WIDTH - windowWidth) // 2}+{((res.HEIGHT - windowHeight) // 2)}')

root.iconbitmap(users.parentPath / "images" / "kanji_icon.ico")

rootscreen = Frame(root, width = width, height = height, bg = '#000000')
rootscreen.pack_propagate(0)
rootscreen.pack()

gameInterface = game.Game_Interface(root, bg = '#555555')

# DEFAULTS:
DEFAULT_GAME_MODE = "vocab"

class main_menu(client.Window):

	def __init__(self, root, **kwargs):

		super().__init__(root, **kwargs)

		self.btnfg = '#ffffff'
		self.btnbg = '#333333'



		mainMenuButtonSize = res.sx(32)
		padding = res.sy(100)

		self.gameButton = self.new_Button(self.mainWin, text = 'Play Flashcards', font = ('arial', mainMenuButtonSize), width = 13, fg = self.btnfg, bg = self.btnbg,
													 command = lambda: self.moveto_window(gameSettings, exec_ = gameSettings.load_defaults),
													 geom = self.set_geom(row = 0, column = 0))
		self.visitLibraryButton = self.new_Button(self.mainWin, text = 'Visit Library', font = ('arial', mainMenuButtonSize), width = 13, fg = self.btnfg, bg = self.btnbg,
																command = lambda: self.moveto_window(libraryInterface, exec_ = libraryInterface.setup_library),
																geom = self.set_geom(row = 1, column = 0, pady = padding))
		self.accountButton = self.new_Button(self.mainWin, text = 'Accounts', font = ('arial', mainMenuButtonSize), width = 13, fg = self.btnfg, bg = self.btnbg,
														 command = lambda: self.moveto_window(AccountsInterface, exec_ = AccountsInterface.load_current_user),
														 geom = self.set_geom(row = 2, column = 0),
														 state = DISABLED)
		self.quitButton = self.new_Button(self.mainWin, text = 'Quit', font = ('arial', mainMenuButtonSize), width = 13, fg = self.btnfg, bg = self.btnbg,
													 command = root.destroy,
													 geom = self.set_geom(row = 3, column = 0, pady = padding))

		allData = cfg.getData()

		self.kanjiData = {'all': allData[0], 'kanji': allData[1], 'size': allData[2], 'hiragana': allData[4], 'katakana': allData[5]}
		self.tagsList = [[inverse_supercode(pair[0]), pair[1]] for pair in allData[3]]

		self.load_window()

	def update_data(self, kanji, data, key):
		if key == 'add':
			self.kanjiData['all'].append(data)
			self.kanjiData['kanji'].append(kanji)
			self.kanjiData['size'] += 1

		elif key == 'delete':
			for allData in [copy for copy in self.kanjiData['all']]:
				if allData[0] == kanji:
					self.kanjiData['all'].remove(allData)
					break
			self.kanjiData['kanji'].remove(kanji)
			self.kanjiData['size'] -= 1

		elif key == 'edit':
			for num, allData in enumerate(self.kanjiData['all']):
				if allData[0] == kanji:
					self.kanjiData['all'][num] = [kanji, encode(data['words']), data['grade'], data['jlpt'], ','.join(data['tags'])] #(1)
					libraryInterface.update_all_data(kanji, data) #(2)
					break

		#all data storage variables:
			#1) mainMenu.kanjiData (dict with keys 'all', 'kanji', 'size')
			#2) libraryInterface.allData (dict with kanji as keys)
			#3) libraryInterface.visualiser.allKanjiFilters (dict with kanji as keys)
			#4) gameSettings.allFlashcards (same as #2)
			#5) gameSettings.filterLabels (class attributes)



mainMenu = main_menu(root, bg = '#000000', shift_y = 0.57)

class library_interface(client.Window):

	engPixels = get_char_pixels(16)

	def __init__(self, root, **kwargs):

		super().__init__(root, **kwargs)

		self.col['hover bd'] = '#7f00ff'
		self.col['hover frame'] = '#0d001a'
		self.col['hover fg'] = '#d580ff'
		self.col['hover tags bg'] = '#0a0911'
		self.col['hover tags fg'] = '#b0bee8'

		self.col['view bd'] = '#3c00ff'
		self.col['view frame'] = '#06001a'
		self.col['view fg'] = '#ffffff'

		self.col['title fg'] = '#a299ff'
		self.col['scroll bg'] = '#009999'

		self.col['buttons bd'] = '#0040ff'
		self.col['buttons frame'] = '#00061a'

		self.col['add popup bd'] = '#33ff33'
		self.col['delete popup bd'] = '#ff3333'
		self.col['edit popup bd'] = '#3333ff'
		self.col['search popup bd'] = '#ffff33'

		self.allData = {data[0]: (decode(data[1]),
										  data[2], 
										  data[3], 
										  data[4].split(',') if data[4] != 'none' else ['none']) 
										  for data in mainMenu.kanjiData['all']}





		self.viewWindow = self.new_Frame(
			self.mainWin,
			width=res.sx(1030),
			height=res.sy(710),
			bg=self.col['view frame'],
			geom=self.set_geom(row=0, column=1, padx=res.sx(5), freeze=1)
		)

		self.buttonsWindow = self.new_Frame(
			self.mainWin,
			width=res.sx(200),
			height=res.sy(700),
			bg=self.col['buttons bd'],
			geom=self.set_geom(row=0, column=2, freeze=1)
		)

		self.buttonsFrameUpper = self.new_Frame(
			self.buttonsWindow,
			width=res.sx(190),
			height=res.sy(125),
			bg=self.col['buttons frame'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5), freeze=1)
		)

		self.addButton = self.new_Button(
			self.buttonsFrameUpper,
			text='Add',
			font=('arial', res.sy(14)),
			width=6,
			command=lambda: self.verify_correct_display('Add', self.addKanjiEditor, self.addButton, '#ffff00'),
			geom=self.set_geom(row=0, column=0, padx=res.sx(7), pady=res.sy(16), ipadx=res.sx(4))
		)

		self.deleteButton = self.new_Button(
			self.buttonsFrameUpper,
			text='Delete',
			font=('arial', res.sy(14)),
			width=6,
			command=lambda: self.verify_correct_display('Delete', self.deleteKanjiEditor, self.deleteButton, '#ff8080'),
			geom=self.set_geom(row=0, column=1, ipadx=res.sx(4))
		)

		self.editButton = self.new_Button(
			self.buttonsFrameUpper,
			text='Edit',
			font=('arial', res.sy(14)),
			width=6,
			command=lambda: self.verify_correct_display('Edit', self.editKanjiEditor, self.editButton, '#00aaff'),
			geom=self.set_geom(row=1, column=0, ipadx=res.sx(4))
		)

		self.displayTypeButton = self.new_Button(
			self.buttonsFrameUpper,
			text='漢字',
			font=('arial', res.sy(14)),
			width=6,
			command=self.change_display_type,
			geom=self.set_geom(row=1, column=1, ipadx=res.sx(4))
		)

		self.buttonsFrameMiddle = self.new_Frame(
			self.buttonsWindow,
			width=res.sx(190),
			height=res.sy(260),
			bg=self.col['buttons frame'],
			geom=self.set_geom(row=1, column=0, freeze=1)
		)

		self.sortByGradeButton = self.new_Button(
			self.buttonsFrameMiddle,
			text='Sort by Grade',
			font=('arial', res.sy(12)),
			bg='#4a2060',
			fg='white',
			width=12,
			command=lambda: self.visualiser.sort_by('grade'),
			geom=self.set_geom(row=0, column=0, padx=res.sx(35), pady=res.sy(5))
		)

		self.sortByJlptButton = self.new_Button(
			self.buttonsFrameMiddle,
			text='Sort by JLPT',
			font=('arial', res.sy(12)),
			bg='#4a2060',
			fg='white',
			width=12,
			command=lambda: self.visualiser.sort_by('jlpt'),
			geom=self.set_geom(row=1, column=0)
		)

		self.sortByDateButton = self.new_Button(
			self.buttonsFrameMiddle,
			text='Sort by Date',
			font=('arial', res.sy(12)),
			bg='#4a2060',
			fg='white',
			width=12,
			command=lambda: self.visualiser.sort_by('date'),
			geom=self.set_geom(row=2, column=0, pady=res.sy(5))
		)

		self.searchingFrame = self.new_Frame(
			self.buttonsFrameMiddle,
			bg=self.col['buttons frame'],
			geom=self.set_geom(row=3, column=0)
		)

		self.searchingEntry = self.new_Entry(
			self.buttonsFrameMiddle,
			font=('arial', res.sy(14)),
			width=12,
			geom=self.set_geom(row=4, column=0, pady=res.sy(5))
		)

		self.visualiser = self.new_visualiser(
			self.viewWindow,
			width=res.sx(1005),
			height=res.sy(485),
			columns={1: 36, 2: 21, 3: 14, 4: 10},
			entry=self.searchingEntry,
			geom=self.set_geom(row=0, column=0)
		)

		self.searchKanjiButton = self.new_radiobutton(
			self.searchingFrame,
			variable=self.visualiser.searchType,
			bg='#6b2e6b',
			value='kanji',
			command=lambda: self.visualiser.select_search_type('kanji'),
			geom=self.set_geom(row=0, column=0)
		)

		self.searchKanaButton = self.new_radiobutton(
			self.searchingFrame,
			variable=self.visualiser.searchType,
			bg='#6b2e6b',
			value='kana',
			command=lambda: self.visualiser.select_search_type('kana'),
			geom=self.set_geom(row=1, column=0)
		)

		self.searchEnglishButton = self.new_radiobutton(
			self.searchingFrame,
			variable=self.visualiser.searchType,
			bg='#6b2e6b',
			value='english',
			command=lambda: self.visualiser.select_search_type('english'),
			geom=self.set_geom(row=2, column=0)
		)

		self.searchKanjiText = self.new_Label(
			self.searchingFrame,
			text='漢字',
			font=('arial', res.sy(12)),
			bg='#6b2e6b',
			fg='white',
			geom=self.set_geom(row=0, column=1)
		)

		self.searchKanaText = self.new_Label(
			self.searchingFrame,
			text='あ',
			font=('arial', res.sy(12)),
			bg='#6b2e6b',
			fg='white',
			geom=self.set_geom(row=1, column=1, pady=res.sy(5))
		)

		self.searchEnglishText = self.new_Label(
			self.searchingFrame,
			text='ABC',
			font=('arial', res.sy(12)),
			bg='#6b2e6b',
			fg='white',
			geom=self.set_geom(row=2, column=1)
		)

		self.buttonsFrameLower = self.new_Frame(
			self.buttonsWindow,
			width=res.sx(190),
			height=res.sy(100),
			bg=self.col['buttons frame'],
			geom=self.set_geom(row=2, column=0, pady=res.sy(5), freeze=1)
		)

		self.backButton = self.new_Button(
			self.buttonsFrameLower,
			text='Back',
			font=('arial', res.sy(14)),
			width=8,
			command=lambda: self.moveto_window(mainMenu, exec_=self.collapse_library),
			geom=self.set_geom(row=4, column=0, padx=res.sx(50), pady=res.sy(30))
		)

		self.kanjiDetailsWin = self.new_Frame(
			self.viewWindow,
			bg='#47536b',
			geom=self.set_geom(row=1, column=0)
		)

		self.kanjiDetailsFrame = self.new_Frame(
			self.kanjiDetailsWin,
			bg='#000000',
			width=res.sx(1020),
			height=res.sy(190),
			geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5), freeze=1)
		)

		self.addKanjiEditor = library_editor.adding_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))
		self.deleteKanjiEditor = library_editor.deleting_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))
		self.editKanjiEditor = library_editor.editing_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))

		self.addHiraganaEditor = library_editor.adding_hiragana_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))
		self.deleteHiraganaEditor = library_editor.deleting_hiragana_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))
		self.editHiraganaEditor = library_editor.editing_hiragana_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))

		self.addKatakanaEditor = library_editor.adding_katakana_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))
		self.deleteKatakanaEditor = library_editor.deleting_katakana_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))
		self.editKatakanaEditor = library_editor.editing_katakana_editor(self.kanjiDetailsWin, width=res.sx(1020), height=res.sy(190))

		self.LowestFrame = self.new_Frame(
			self.buttonsWindow,
			bg='black',
			width=res.sx(190),
			height=res.sy(190),
			geom=self.set_geom(row=3, column=0, freeze=1)
		)

		self.enlargedKanjiLabel = self.new_Label(
			self.LowestFrame,
			text='',
			bg='black',
			fg='white',
			geom=self.set_geom(row=0, column=0)
		)

		self.gradeTitle = self.new_Label(
			self.kanjiDetailsFrame,
			font=('arial', res.sy(16)),
			bg='#000000',
			fg='#ffff00',
			width=8,
			anchor='w',
			geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5))
		)

		self.jlptTitle = self.new_Label(
			self.kanjiDetailsFrame,
			font=('arial', res.sy(16)),
			bg='#000000',
			fg='#ffff00',
			width=8,
			anchor='w',
			geom=self.set_geom(row=0, column=1)
		)

		self.tagsTitle = self.new_Label(
			self.kanjiDetailsFrame,
			font=('arial', res.sy(16)),
			bg='#000000',
			fg='#ffff00',
			width=40,
			anchor='w',
			geom=self.set_geom(row=0, column=2, padx=res.sx(5))
		)

		self.wordsFrame = self.new_Frame(
			self.kanjiDetailsFrame,
			bg='#000000',
			geom=self.set_geom(row=1, column=0, padx=res.sx(5), pady=res.sy(5), columnspan=3, sticky='w')
		)

		self.kanaLabel = self.new_Label(
			self.wordsFrame,
			bg='#000000',
			fg='#ffff00',
			font=('arial', res.sy(16)),
			geom=self.set_geom(row=0, column=0, padx=res.sx(2), pady=res.sy(2))
		)

		self.englishLabel = self.new_Label(
			self.wordsFrame,
			bg='#000000',
			fg='#ffff00',
			font=('arial', res.sy(16)),
			geom=self.set_geom(row=0, column=1, padx=res.sx(2))
		)






	def verify_correct_display(self, key, *args):
		if self.currentDisplayType == 'kanji':
			self.prompt_kanji_editor(key, *args)

		elif self.currentDisplayType == 'hiragana':
			self.prompt_hiragana_editor(key, *args)

		else:
			self.prompt_katakana_editor(key, *args)

	def prompt_kanji_editor(self, key, editor, button, bg):
		if self.activePopup == key:
			self.close_kanji_popup()
		elif self.activePopup == '':
			self.load_editor(editor, button, key)
			self.activate_popup(bg, key)
		else:
			self.unload_active_editor(self.activePopup)
			self.activate_popup(bg, key)
			self.load_editor(editor, button, key)

	def prompt_hiragana_editor(self, key, *args):
		if self.activePopup == key:
			self.load_widgets(self.kanjiDetailsFrame)
			self.unload_hiragana_editor(key)

		elif self.activePopup == '':
			self.unload_widgets(self.kanjiDetailsFrame)
			self.load_hiragana_editor(key)

		else:
			self.unload_hiragana_editor(self.activePopup)
			self.load_hiragana_editor(key)

	def load_hiragana_editor(self, key):
		editor = {'Add': self.addHiraganaEditor, 'Delete': self.deleteHiraganaEditor, 'Edit': self.editHiraganaEditor}[key]
		button = {'Add': self.addButton, 'Delete': self.deleteButton, 'Edit': self.editButton}[key]
		editor.load(invoke = self.addHiraganaEditor.get_interface)
		button.config(text = 'Cancel', bg = '#ff4d4d')
		self.activePopup = key

		if self.activePopup == 'Add':
			self.setup_new_hiragana_variables()

	def unload_hiragana_editor(self, key):
		editor = {'Add': self.addHiraganaEditor, 'Delete': self.deleteHiraganaEditor, 'Edit': self.editHiraganaEditor}[key]
		button = {'Add': self.addButton, 'Delete': self.deleteButton, 'Edit': self.editButton}[key]
		editor.unload(invoke = self.addHiraganaEditor.collapse)
		button.config(text = key, bg = '#f0f0f0')
		self.activePopup = ''

		if key == 'Add':
			self.forfeit_new_hiragana()

	def setup_new_hiragana_variables(self):
		self.visualiser.create_new_label(scripture = 'hiragana')
		kanaEntry, kanjiEntry = self.addHiraganaEditor.newKanaEntry, self.addHiraganaEditor.newKanjiEntry
		kanaVar = self.addHiraganaEditor.hiraganaTranslator.textVar
		kanaVar.trace_add('write', lambda *args: self.visualiser.update_new_hiragana_label(kanaEntry, kanjiEntry))

		for num, engEntry in enumerate(self.addHiraganaEditor.newMeaningEntries):
			engvar = self.addHiraganaEditor.newMeaningVars[num]
			engvar.trace_add('write', lambda *args, num = num, engEntry = engEntry: self.visualiser.collate_new_meanings(num, engEntry))

		kanjiVar = self.addHiraganaEditor.newKanjiVar
		kanjiVar.trace_add('write', lambda *args: self.visualiser.update_new_hiragana_label(kanaEntry, kanjiEntry))

	def forfeit_new_hiragana(self):
		self.visualiser.cancel_new_kana(*self.addHiraganaEditor.get_vars())
		self.addHiraganaEditor.clear_all_entries()

	def confirm_add_new_hiragana(self):
		newData = self.addHiraganaEditor.get_new_hiragana()

		if not ('' in newData[:2]) and not (newData[0] in self.visualiser.allHiragana):
			cfg.add_new_hiragana(*newData)
			self.visualiser.add_new_hiragana(*newData)
			self.addHiraganaEditor.clear_all_entries()

	def prompt_katakana_editor(self, key, *args):
		if self.activePopup == key:
			self.load_widgets(self.kanjiDetailsFrame)
			self.unload_katakana_editor(key)

		elif self.activePopup == '':
			self.unload_widgets(self.kanjiDetailsFrame)
			self.load_katakana_editor(key)

		else:
			self.unload_katakana_editor(self.activePopup)
			self.load_katakana_editor(key)

	def load_katakana_editor(self, key):
		editor = {'Add': self.addKatakanaEditor, 'Delete': self.deleteKatakanaEditor, 'Edit': self.editKatakanaEditor}[key]
		button = {'Add': self.addButton, 'Delete': self.deleteButton, 'Edit': self.editButton}[key]
		editor.load(invoke = editor.get_interface)
		button.config(text = 'Cancel', bg = '#ff4d4d')
		self.activePopup = key

		if self.activePopup == 'Add':
			self.setup_new_katakana_variables()

	def unload_katakana_editor(self, key):
		editor = {'Add': self.addKatakanaEditor, 'Delete': self.deleteKatakanaEditor, 'Edit': self.editKatakanaEditor}[key]
		button = {'Add': self.addButton, 'Delete': self.deleteButton, 'Edit': self.editButton}[key]
		editor.unload(invoke = editor.collapse)
		button.config(text = key, bg = '#f0f0f0')
		self.activePopup = ''

		if key == 'Add':
			self.forfeit_new_katakana()

	def setup_new_katakana_variables(self):
		self.visualiser.create_new_label(scripture = 'katakana')
		kanaEntry = self.addKatakanaEditor.newKanaEntry
		kanaVar = self.addKatakanaEditor.katakanaTranslator.textVar
		kanaVar.trace_add('write', lambda *args: self.visualiser.update_new_katakana_label(kanaEntry))

		for num, engEntry in enumerate(self.addKatakanaEditor.newMeaningEntries):
			engvar = self.addKatakanaEditor.newMeaningVars[num]
			engvar.trace_add('write', lambda *args, num = num, engEntry = engEntry: self.visualiser.collate_new_meanings(num, engEntry))

	def forfeit_new_katakana(self):
		self.visualiser.cancel_new_kana(*self.addKatakanaEditor.get_vars())
		self.addKatakanaEditor.clear_all_entries()

	def confirm_add_new_katakana(self):
		newData = self.addKatakanaEditor.get_new_katakana()

		if not ('' in newData) and not (newData[0] in self.visualiser.allKatakana):
			cfg.add_new_katakana(*newData)
			self.visualiser.add_new_katakana(*newData)
			self.addKatakanaEditor.clear_all_entries()

	def confirm_add_new_hiragana(self):
		newData = self.addHiraganaEditor.get_new_hiragana()

		if not ('' in newData[:2]) and not (newData[0] in self.visualiser.allHiragana):
			cfg.add_new_hiragana(*newData)
			self.visualiser.add_new_hiragana(*newData)
			self.addHiraganaEditor.clear_all_entries()

	def close_kanji_popup(self):
		self.unload_active_editor(self.activePopup)
		self.load_widgets(self.kanjiDetailsFrame)
		self.deactivate_popup()

	def activate_popup(self, fg, popup):
		self.labelHoverFg = fg
		self.activePopup = popup
		if self.selectedKanji != '':
			self.enlarge_hover_hide(self.selectedKanji, bypass = True)
			self.unfreeze_kanji(self.selectedKanji)

	def deactivate_popup(self):
		self.labelHoverFg = '#ffff00'
		self.activePopup = ''

	def load_editor(self, editor, button, text):
		editor.load(invoke = editor.get_interface)
		button.config(text = 'Cancel', bg = '#ff4d4d')
		self.activePopup = text

	def unload_active_editor(self, text):
		if self.selectedKanji == '_DELETING_':
			for kanji in self.deleteKanjiEditor.pendingDict:
				self.remove_highlight(kanji)
			self.reset_selected_kanji()
		elif self.selectedKanji == '_EDITING_':
			self.remove_highlight(self.editKanjiEditor.editingKanji)
			self.reset_selected_kanji()
		self.hide_active_editor(text)
		self.selectedKanji = ''

	def hide_active_editor(self, text):
		activeEditor = {'Add': self.addKanjiEditor, 'Delete': self.deleteKanjiEditor, 'Edit': self.editKanjiEditor}[text]
		activeButton = {'Add': self.addButton, 'Delete': self.deleteButton, 'Edit': self.editButton}[text]
		activeEditor.unload(self.kanjiDetailsFrame, invoke = activeEditor.collapse)
		activeButton.config(bg = '#f0f0f0', text = self.activePopup)

	def reset_selected_kanji(self):
		self.selectedKanji = ''
		self.configure_hover_display('')

	def change_display_type(self):
		#cycles from viewing kanji, kana phrases and katakana words.
		nextType = {'kanji': 'hiragana', 'hiragana': 'katakana', 'katakana': 'kanji'}[self.currentDisplayType]
		buttonText = {'kanji': '漢字', 'hiragana': 'ひらがな', 'katakana': 'カタカナ'}[nextType]
		self.displayTypeButton.config(text = buttonText)
		self.currentDisplayType = nextType

		#cancel any active popup
		if self.activePopup != '':
			self.close_kanji_popup()

		if nextType == 'hiragana':
			self.visualiser.swap_visualisers('hiragana')

		elif nextType == 'katakana':
			self.visualiser.swap_visualisers('katakana')

		else:
			self.visualiser.swap_visualisers('kanji')

	def setup_library(self):
		data = {data[0]: {'words': decode(data[1]), 'grade': data[2], 'jlpt': data[3], 'date': num} for (num, data) in enumerate(mainMenu.kanjiData['all'], start = 1)}
		self.visualiser.setup_data(kanjidata = data,
											hiragana_data = mainMenu.kanjiData['hiragana'],
											katakana_data = mainMenu.kanjiData['katakana'],
										   enterLabel = self.enlarge_hover_display,
											leaveLabel = self.enlarge_hover_hide,
											leftclick = self.select_kanji)

		self.activePopup = ''
		self.selectedKanji = ''
		self.labelHoverFg = '#ffff00'

		self.currentDisplayType = 'kanji'

		self.addKanjiEditor.setup_library_info([kanji for kanji in data], invokeExist = self.highlight, 
																								cancelInvokeExist = self.remove_highlight,
																								previewInvoke = self.start_preview)

		self.deleteKanjiEditor.setup_library_info([kanji for kanji in data], clearinvoke = self.clear_deleting_highlight,
																									deleteinvoke = self.confirm_delete_kanji)

		self.editKanjiEditor.setup_library_info([kanji for kanji in data], selectinvoke = self.select_edit,
																								 deselectinvoke = self.deselect_edit,
																								 previewinvoke = self.preview_edit)

		self.addHiraganaEditor.setup(addinvoke = self.confirm_add_new_hiragana)
		self.addKatakanaEditor.setup(addinvoke = self.confirm_add_new_katakana)

		self.addKatakanaEditor

	def select_edit(self, kanji):
		if self.selectedKanji != '_EDITING_':
			self.highlight(kanji, highlightcolour = '#0080ff')
			self.enlargedKanjiLabel.config(fg = '#0080ff')

	def deselect_edit(self, kanji):
		self.enlargedKanjiLabel.config(fg = '#000000', text = '')
		self.remove_highlight(kanji)
		self.selectedKanji = ''
		self.configure_hover_display('')

	def preview_edit(self, kanji, changes):

		# grid the edit and cancel button on the extreme right, which will call the cancel preview function.
		self.confirmEditButton = Button(
			self.kanjiDetailsFrame,
			text='UPDATE',
			font=('arial', res.sy(18)),
			bg='#262626',
			fg='#cdcde4',
			width=8,
			command=lambda: self.confirm_edit_kanji(kanji, changes)
		)
		self.cancelPreviewButton = Button(
			self.kanjiDetailsFrame,
			text='CANCEL',
			font=('arial', res.sy(18)),
			bg='#262626',
			fg='#e4cdcd',
			width=8,
			command=self.cancel_edit_preview
		)

		self.confirmEditButton.grid(
			row=0,
			column=4,
			padx=res.sx(175),
			pady=res.sy(23),
			sticky='se',
			rowspan=2
		)
		self.cancelPreviewButton.grid(
			row=2,
			column=4,
			sticky='s'
		)

		#manually update the display window interface to show the edited information
		self.gradeTitle.config(text = f"Grade: {changes['grade']}")
		self.jlptTitle.config(text = f"JLPT: {changes['jlpt']}")
		self.tagsTitle.config(text = f"Tags: {', '.join(changes['tags'])}")
		kanaText = format_kana([kana for kana in changes['words']], 4)
		engText = format_english([changes['words'][kana] for kana in changes['words']], self.engPixels, res.sx(900))
		self.kanaLabel.config(text = kanaText)
		self.englishLabel.config(text = engText)

		#change the edit kanji interface to the display kanji info interface, which will show all the kanji info.
		self.editKanjiEditor.unload()
		self.load_widgets(self.kanjiDetailsFrame)
		self.debug_displayFrame()

	def cancel_edit_preview(self):
		self.unload_widgets(self.kanjiDetailsFrame)
		self.editKanjiEditor.load()
		self.destroy_temp_buttons(self.confirmEditButton, self.cancelPreviewButton)

	def confirm_edit_kanji(self, kanji, changes):
		#--------------UPDATE THE DATABASE AND ALL OTHER NECESSARY PARTS OF THE PROGRAM--------------
		cfg.edit_data(kanji = kanji, words = encode(changes['words']),
											  grade = changes['grade'],
											  jlpt = changes['jlpt'],
											  tags = ','.join(changes['tags'])
											  )

		mainMenu.update_data(kanji, changes, 'edit')

		#return to editing screen with clear entries and deselect current editing kanji.
		self.unload_widgets(self.kanjiDetailsFrame)
		self.editKanjiEditor.load()
		self.destroy_temp_buttons(self.confirmEditButton, self.cancelPreviewButton)

		self.editKanjiEditor.get_edit_variables()
		self.selectedKanji = ''

		self.enlarge_hover_hide(kanji)
		self.remove_highlight(kanji)
		self.editKanjiEditor.refresh_edit_editor()

	def update_all_data(self, kanji, data):
		self.allData[kanji] = (data['words'], data['grade'], data['jlpt'], data['tags'])

	def destroy_temp_buttons(self, *buttons):
		for button in buttons:
			button.destroy()
			del button

	def clear_deleting_highlight(self, kanji):
		self.remove_highlight(kanji)

	def confirm_delete_kanji(self, deletelist):
		self.visualiser.shift_after_deleting(deletelist)

		for kanji in deletelist:
			cfg.remove_from_database(kanji)
			self.addKanjiEditor.existingKanji.remove(kanji)
			mainMenu.update_data(kanji, '', 'delete')

	def cancel_add_preview(self, *args):
		self.enlarge_hover_hide(args[0], bypass = True)
		self.visualiser.cancel_new_label_preview(*args)
		self.unload_widgets(self.kanjiDetailsFrame)
		self.addKanjiEditor.load()
		self.destroy_temp_buttons(self.confirmAddButton, self.cancelPreviewButton)

	def confirm_add_new_kanji(self, newKanji, newWords, kanjiData):
		self.enlarge_hover_hide(newKanji, bypass = True)
		self.remove_highlight(newKanji)
		self.destroy_temp_buttons(self.confirmAddButton, self.cancelPreviewButton)

		#add new kanji into the database.
		updatedNewData = cfg.add_to_database(newKanji, newWords, kanjiData['grade'], kanjiData['jlpt'], ','.join(kanjiData['tags']))

		#update main menu all data
		mainMenu.update_data(newKanji, updatedNewData, 'add')
		self.addKanjiEditor.existingKanji.append(newKanji)

		#return to adding scrren (refreshed)

		self.addKanjiEditor.reset_kanji_details()
		self.addKanjiEditor.get_interface()

		self.addKanjiEditor.load()
		self.destroy_temp_buttons(self.confirmAddButton, self.cancelPreviewButton)

	def start_preview(self, *args):
		kanji = args[0]
		data = args[1]
		#when a new kanji is getting previewed, this function is called to get it's position among all existing kanji, based on current sorting type.
		label_shifts = self.visualiser.preview_new_label(*args)

		words = [tuple(List) for List in data['words']]
		engsList = []
		for engs in words[1]:
			engSplit = []
			for eng in engs.split(','):
				if eng != '':
					engSplit.append(eng)
			engsList.append(engSplit)

		wordsDict = {kana: eng for (kana, eng) in zip(words[0], engsList)}

		#temporarily save the new kanji in self.allData
		self.allData[kanji] = (wordsDict, data['grade'], data['jlpt'], data['tags'])
		self.enlarge_hover_display(kanji, bypass = True)
		self.highlight(kanji, highlightcolour = '#00ff00')

		#grid the confirm and cancel button on the extreme right, which will call the cancel preview function.
		self.confirmAddButton = Button(self.kanjiDetailsFrame, text = 'CONFIRM', font = ('arial', res.sy(18)),  bg = '#262626', fg = '#cde4cd', width = res.sx(8),
													 command = lambda: self.confirm_add_new_kanji(kanji, wordsDict, data))
		self.cancelPreviewButton = Button(self.kanjiDetailsFrame, text = 'CANCEL', font = ('arial', res.sy(18)), bg = '#262626', fg = '#e4cdcd', width = res.sx(8),
		 							 				 command = lambda: self.cancel_add_preview(kanji, *label_shifts))

		self.confirmAddButton.grid(row = 0, column = 4, padx = res.sx(175), pady = res.sy(23), sticky = 'se', rowspan = 2)
		self.cancelPreviewButton.grid(row = 2, column = 4, sticky = 's')

		#change the add kanji interface to the display kanji info interface, which will show all the kanji info.
		self.addKanjiEditor.unload()
		self.load_widgets(self.kanjiDetailsFrame)
		self.debug_displayFrame()
		return label_shifts

	def get_special_hover_case(self, kanji, path):
		size = {1: res.sy(135), 2: res.sy(68), 3: res.sy(46), 4: res.sy(34)}[len(kanji)]
		pady = {1: 0, 2: res.sy(35), 3: res.sy(55), 4: res.sy(65)}[len(kanji)]
		if (self.activePopup == 'Delete') and (kanji in self.deleteKanjiEditor.pendingDict):
			self.selectedKanji = '_DELETING_'
			self.enlargedKanjiLabel.config(text = kanji if (path == 'enter') else '', font = ('times', size), pady = pady, fg = '#ff0000')
			return False
		elif (self.activePopup == 'Edit') and (self.editKanjiEditor.editingKanji != ''):
			self.selectedKanji = '_EDITING_'
			return False
		return True

	def enlarge_hover_display(self, *args, bypass = False):
		kanji = args[0]
		specialCase = self.get_special_hover_case(kanji, 'enter') if self.activePopup in ('Delete', 'Edit') else False
		if (self.activePopup != 'Add' and self.selectedKanji == '') or (specialCase is True) or (bypass is True):
			length = len(kanji)
			size = {1: res.sy(135), 2: res.sy(68), 3: res.sy(46), 4: res.sy(34)}[len(kanji)]
			pady = {1: 0, 2: res.sy(35), 3: res.sy(55), 4: res.sy(65)}[len(kanji)]
			fg = {1: '#ffffff', 2: '#80ff80', 3: '#80ffff', 4: '#ff80ff'}[length]
			self.enlargedKanjiLabel.config(text = kanji, font = ('times', size), pady = pady, fg = fg)
			self.visualiser.highlight_label_fg(kanji, self.labelHoverFg)
			self.configure_hover_display(kanji, bypass)

	def enlarge_hover_hide(self, *args, bypass = False):
		kanji = args[0]
		specialCase = self.get_special_hover_case(kanji, 'leave') if self.activePopup in ('Delete', 'Edit') else False
		if (self.activePopup != 'Add' and self.selectedKanji == '') or (specialCase is True) or (bypass is True):
			fg = {1: '#ffffff', 2: '#80ff80', 3: '#80ffff', 4: '#ff80ff'}[len(kanji)]
			self.visualiser.highlight_label_fg(kanji, fg)
			self.enlargedKanjiLabel.config(text = '')
			self.configure_hover_display('', bypass)

	def configure_hover_display(self, kanji, bypass = False):
		if (self.activePopup != 'Add' and self.selectedKanji) == '' or (bypass is True):
			self.gradeTitle.config(text = '' if kanji == '' else f'Grade: {self.allData[kanji][1]}')
			self.jlptTitle.config(text = '' if kanji == '' else f'JLPT: {self.allData[kanji][2]}')
			self.tagsTitle.config(text = '' if kanji == '' else f"Tag(s): {', '.join(self.allData[kanji][3])}")

			if kanji != '':
				words = self.allData[kanji][0]
				kanaText = format_kana([kana for kana in words], 4)
				engText = format_english([words[kana] for kana in words], self.engPixels, 900)

				self.kanaLabel.config(text = kanaText)
				self.englishLabel.config(text = engText)

			else:
				self.kanaLabel.config(text = '')
				self.englishLabel.config(text = '')

	def debug_displayFrame(self):
		self.kanjiDetailsFrame.config(width = 1020) #<- weird bug with weird fix.

	def configure_deleting_selection(self, kanji):
		inPending = self.deleteKanjiEditor.select_deleting_kanji(kanji)

		if inPending:
			self.highlight(kanji, highlightcolour = '#ff0000')
			# self.visualiser.disable_hover_interaction(kanji)

		else:
			self.highlight(kanji, highlightcolour = '#ff8080', bold = False)
			# self.visualiser.enable_hover_interaction(kanji)

		return inPending

	def configure_editing_selection(self, kanji):
		if self.selectedKanji != '_EDITING_':
			colours = {pair[0]: pair[1] for pair in mainMenu.tagsList}
			self.editKanjiEditor.select_editing_kanji(kanji, self.allData[kanji], colours)


	def select_kanji(self, *args):
		kanji = args[0]
		if self.activePopup == 'Delete':
			deletingKanji = self.configure_deleting_selection(kanji)
			self.enlargedKanjiLabel.config(fg = '#ff0000' if deletingKanji else '#ffffff')

		elif self.activePopup == 'Edit':
			self.configure_editing_selection(kanji)

		elif self.activePopup == '':
			self.highlight_selected_kanji(kanji)

	def highlight_selected_kanji(self, kanji):
		if self.selectedKanji == kanji:
			self.unfreeze_kanji(kanji, stillHovering = True)
		elif self.selectedKanji == '':
			self.freeze_kanji(kanji)
		else:
			self.unfreeze_kanji(self.selectedKanji)
			self.freeze_kanji(kanji)
			self.enlarge_hover_display(kanji, bypass = True)

	def freeze_kanji(self, kanji):
		self.modify_label_viewing(kanji, fg = self.labelHoverFg, bold = True)
		self.selectedKanji = kanji
		
	def unfreeze_kanji(self, kanji, stillHovering = False):
		fg = self.labelHoverFg if (stillHovering is True) else {1: '#ffffff', 2: '#80ff80', 3: '#80ffff', 4: '#ff80ff'}[len(kanji)]
		self.modify_label_viewing(kanji, fg = fg, bold = False)
		self.selectedKanji = ''

	def modify_label_viewing(self, kanji, fg, bold):
		label = self.visualiser.allKanjiLabels[kanji]
		ipadding = 0 if (bold is True) else 1
		label.config(fg = fg, font = ('helvatica', 14, ('bold' if (bold is True) else 'normal')))
		label.grid_configure(ipadx = ipadding, ipady = ipadding)

	def highlight(self, kanji, **kwargs):
		fg = kwargs['highlightcolour'] if 'highlightcolour' in kwargs else '#ff0000'
		self.modify_label_viewing(kanji, fg, bold = kwargs['bold'] if 'bold' in kwargs else True)

	def remove_highlight(self, kanji):
		fg = {1: '#ffffff', 2: '#80ff80', 3: '#80ffff', 4: '#ff80ff'}[len(kanji)]
		self.modify_label_viewing(kanji, fg, bold = False)

	def collapse_library(self):
		if self.activePopup != '':
			self.unload_active_editor(self.activePopup)
		for frame in self.visualiser.kanjiLengthFrames:
			frame.destroy()

libraryInterface = library_interface(root, bg = '#000000')

class gameSettings_interface(client.Window):

	def __init__(self, root, **kwargs):

		super().__init__(root, **kwargs)

		self.col['modesbg'] = '#33004d'

		self.col['modebtnbg'] = '#7000a8'
		self.col['modebtnfg'] = '#80ffff'

		self.col['filtermain'] = '#080033'
		self.col['filterbg'] = '#120e25'
		self.col['filterwin'] = '#aa99ff'

		self.col['inactive grade'] = '#392d53'
		self.col['inactive jlpt'] = '#2d2d53'
		self.col['inactive length'] = '#2d3953'

		self.col['active grade'] = '#835cd6'
		self.col['active jlpt'] = '#5c5cd6'
		self.col['active length'] = '#5c85d6'

		self.col['tags btn'] = '#2e576b'
		self.col['disp tags win'] = '#bee2f4'
		self.col['disp tags bg'] = '#121212'

		self.col['shown bg'] = '#b5afcf'
		self.col['all bg'] = '#caafcf'

		self.col['inc fg'] = '#00004d'
		self.col['exc fg'] = '#4d0000'

		self.col['labelfg'] = '#cbcbcb'
		self.col['highlightfg'] = '#111111'

		self.col['or logicbg'] = '#3a3a78'
		self.col['and logicbg'] = '#783a3a'

		self.col['transitionsbg'] = '#001933'
		self.col['diffbg'] = '#003326'
		self.col['timerbg'] = '#80ffdf'
		self.col['lifebg'] = '#80ffff'
		self.col['recoverbg'] = '#80dfff'
		self.col['repetitionbg'] = '#ff99ff'
		self.col['defaultbg'] = '#2a00ff'

		self.col['inactive btn bg'] = '#f0f0f0'

		self.col['active language fg'] = '#000080'
		self.col['active language bg'] = '#80bfff'

		self.col['inactive language fg'] = '#80bfff'
		self.col['inactive language bg']= '#000000'

		self.col['new preset bg'] = '#b3d9e6'
		self.col['open presets bg'] = '#b3c8e6'





		#main frame containing game type buttons
		self.modesWindow = self.new_Frame(self.mainWin, bg=self.col['modesbg'], width=res.sx(150), height=res.sy(500),
													 geom=self.set_geom(row=0, column=0, padx=res.sx(10), sticky=N, freeze=1))

		self.modesFrame = self.new_Frame(self.modesWindow, bg=self.col['modesbg'], width=res.sx(150), height=res.sy(500),
													 geom=self.set_geom(row=0, column=0, freeze=1))

		self.vocabModeButton = self.new_Button(self.modesFrame, text='Vocab', font=('arial', res.sy(20)), width=res.sx(7), state = DISABLED,
															bg=self.col['modebtnbg'], fg=self.col['modebtnfg'],
															command=lambda: self.set_game_mode('vocab'),
															geom=self.set_geom(row=0, column=0, padx=res.sx(7), pady=res.sy(10)))
		self.writingModeButton = self.new_Button(self.modesFrame, text='Writing', font=('arial', res.sy(20)), width=res.sx(7), state = DISABLED,
															  bg=self.col['modebtnbg'], fg=self.col['modebtnfg'],
															  command=lambda: self.set_game_mode('writing'),
															  geom=self.set_geom(row=1, column=0, pady=res.sy(10)))

		self.showKanaButton = self.new_Button(self.modesFrame, text='Show Kana:\nYes', font=('arial', res.sy(15)), state = DISABLED,
														  bg=self.col['modebtnbg'], fg=self.col['modebtnfg'],
														  command=self.writing_toggle_showing_kana,
														  geom=self.set_geom(row=2, column=0, pady=res.sy(10)))

		self.gamemodeFrame = self.new_Frame(self.modesFrame, bg=self.col['modesbg'], width=res.sx(140), height=res.sy(100),
														geom=self.set_geom(row=3, column=0, padx=res.sx(7), pady=res.sy(195), freeze=1))

		self.gamemodeTitle = self.new_Label(self.gamemodeFrame, font=('arial', res.sy(16)), width=res.sx(10),
														bg='#191221', fg='yellow',
														geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5), ipady=res.sy(10)))


		#main frame containing various filtering options for selecting kanji
		self.filterWindow = self.new_Frame(self.mainWin, bg=self.col['filtermain'], width=res.sx(1000), height=res.sy(800),
													  geom=self.set_geom(row=0, column=1, freeze=1))

		self.showFiltersWindow = self.new_Frame(self.filterWindow, bg=self.col['filterwin'], width=res.sx(230), height=res.sy(715),
															 geom=self.set_geom(row=1, column=0, padx=res.sx(10), freeze=1))

		self.viewFiltersFrame = ScrollingFrame(self.mainWin, self.showFiltersWindow, bg='#000000', width = 220, height = 705, increments=1)
		self.viewerFrame = self.viewFiltersFrame.canvasFrame

		self.widgets.append({'widget': self.viewFiltersFrame, 'geometry': {'row': 1, 'column': 0, 'padx': res.sx(5), 'pady': res.sy(5), 'freeze': 0, 'hidden': 0, 'scrollframe': 1, 'loader': None}})

		self.filterTotalFrame = self.new_Frame(self.filterWindow, width=res.sx(230), height=res.sy(50), bg=self.col['filterwin'],
															geom=self.set_geom(row=0, column=0, pady=res.sy(10), freeze=1))
		self.filterTotalLabel = self.new_Label(self.filterTotalFrame, text='', font=('arial', res.sy(20)), bg='#000000', fg='#ffffff', width=res.sx(13), anchor=W,
															geom=self.set_geom(row=0, column=0, padx=res.sx(4), pady=res.sy(3), ipadx=res.sx(4), ipady=res.sy(3)))

		self.filterCheckButtonsFrame = self.new_Frame(self.filterWindow, width=res.sx(400), height=res.sy(465), bg=self.col['filterwin'],
																	 geom=self.set_geom(row=0, column=1, rowspan=2, sticky=NW, pady=res.sy(10), freeze=1))

		self.filterGradeWindow = self.new_Frame(self.filterCheckButtonsFrame, width=res.sx(390), height=res.sy(110), bg=self.col['filterbg'],
															 geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5), freeze=1))

		self.filterGradeTitle = self.new_Label(self.filterGradeWindow, text='Filter Grade(s)', font=('arial', res.sy(20)), 
															bg=self.col['filterbg'], fg=self.col['labelfg'],
															geom=self.set_geom(row=0, column=0, pady=res.sy(8)))

		self.gradeButtonsFrame = self.new_Frame(self.filterGradeWindow, bg=self.col['filterbg'],
															 geom=self.set_geom(row=1, column=0, padx=res.sx(6), columnspan=2))

		self.gradeButtons = {grade: self.new_Button(self.gradeButtonsFrame, text=grade, font=('arial', res.sy(15)), width=res.sx(3), 
											 bg=self.col['inactive grade'], fg=self.col['labelfg'],
											 command=lambda grade=grade: self.adjust_filter('grade', grade),
											 geom=self.set_geom(row=1, column=num, padx=res.sx(4) if num % 2 == 0 else 0, pady=res.sy(4) if num == 0 else 0))
											 for num, grade in enumerate(('1', '2', '3', '4', '5', '6', 'JH', '-'))}

		self.gradeLogicButton = self.new_Button(self.filterGradeWindow, font=('arial', res.sy(16)), fg=self.col['labelfg'], width=res.sx(10),
															 geom=self.set_geom(row=0, column=1, sticky=E, padx=res.sx(7)))

		self.filterJlptWindow = self.new_Frame(self.filterCheckButtonsFrame, width=res.sx(390), height=res.sy(110), bg=self.col['filterbg'],
															geom=self.set_geom(row=1, column=0, freeze=1))

		self.filterJlptTitle = self.new_Label(self.filterJlptWindow, text='Filter JLPT(s)', font=('arial', res.sy(20)), 
														  bg=self.col['filterbg'], fg=self.col['labelfg'],
														  geom=self.set_geom(row=0, column=0, pady=res.sy(8)))

		self.jlptButtonsFrame = self.new_Frame(self.filterJlptWindow, bg=self.col['filterbg'],
															 geom=self.set_geom(row=1, column=0, padx=res.sx(45), columnspan=2))				

		self.jlptButtons = {jlpt: self.new_Button(self.jlptButtonsFrame, text=jlpt, font=('arial', res.sy(16)), width=res.sx(3),
										  bg=self.col['inactive jlpt'], fg=self.col['labelfg'],
										  command=lambda jlpt=jlpt: self.adjust_filter('jlpt', jlpt),
										  geom=self.set_geom(row=1, column=num, padx=res.sx(4) if num % 2 == 0 else 0, pady=res.sy(4) if num == 0 else 0))
										  for num, jlpt in enumerate(('N5', 'N4', 'N3', 'N2', 'N1', '-'))}

		self.jlptLogicButton = self.new_Button(self.filterJlptWindow, font=('arial', res.sy(16)), fg=self.col['labelfg'], width=res.sx(10),
															 geom=self.set_geom(row=0, column=1, padx=res.sx(7), sticky=E))






		self.filterLengthWindow = self.new_Frame(self.filterCheckButtonsFrame, width=res.sx(390), height=res.sy(110), bg=self.col['filterbg'],
															  geom=self.set_geom(row=2, column=0, pady=res.sy(5), freeze=1))

		self.filterLengthTitle = self.new_Label(self.filterLengthWindow, text='Filter Length(s)', font=('arial', res.sy(20)), 
															 bg=self.col['filterbg'], fg=self.col['labelfg'],
															 geom=self.set_geom(row=0, column=0, pady=res.sy(8)))

		self.lengthButtonsFrame = self.new_Frame(self.filterLengthWindow, bg=self.col['filterbg'],
															  geom=self.set_geom(row=1, column=0, padx=res.sx(91), columnspan=2))  

		self.lengthButtons = {length: self.new_Button(self.lengthButtonsFrame, text=length, font=('arial', res.sy(16)), width=res.sx(3),
												bg=self.col['inactive length'], fg=self.col['labelfg'],
												command=lambda length=length: self.adjust_filter('length', length),
												geom=self.set_geom(row=1, column=num, padx=res.sx(4) if num % 2 == 0 else 0, pady=res.sy(4) if num == 0 else 0))
												for num, length in enumerate(('1', '2', '3', '4+'))}

		self.lengthLogicButton = self.new_Button(self.filterLengthWindow, font=('arial', res.sy(16)), fg=self.col['labelfg'], width=res.sx(10),
															 geom=self.set_geom(row=0, column=1, sticky=E))


		self.filterTagsWindow = self.new_Frame(self.filterCheckButtonsFrame, width=res.sx(390), height=res.sy(110), bg=self.col['filterbg'],
															geom=self.set_geom(row=3, column=0, freeze=1))

		self.filterTagsTitle = self.new_Label(self.filterTagsWindow, text='Filter Tag(s)', font=('arial', res.sy(20)), 
															 bg=self.col['filterbg'], fg=self.col['labelfg'],
															 geom=self.set_geom(row=0, column=0, padx=res.sx(10), pady=res.sy(12)))


		self.filterTagsButton = self.new_Button(self.filterTagsWindow, text='Tags', font=('arial', res.sy(16)),
															 bg=self.col['tags btn'], fg=self.col['labelfg'],
															 command=lambda: open_tags_window(mainMenu.tagsList, bg='#0d0613', invoke=self.update_tag_filter),
															 geom=self.set_geom(row=0, column=1, padx=res.sx(5)))

		self.tagsLogicButton = self.new_Button(self.filterTagsWindow, font=('arial', res.sy(16)), width=res.sx(10), fg=self.col['labelfg'],
															geom=self.set_geom(row=0, column=2, padx=res.sx(5)))

		self.displayTagsWindow = self.new_Frame(self.filterTagsWindow, bg=self.col['disp tags win'], width=res.sx(218), height=res.sy(40),
															 geom=self.set_geom(row=1, column=0, columnspan=2, padx=res.sx(5), freeze=1))

		self.displayTagsFrame = self.new_Frame(self.displayTagsWindow, bg=self.col['disp tags bg'], width=res.sx(216), height=res.sy(38),
															geom=self.set_geom(row=0, column=0, padx=res.sx(1), pady=res.sy(1), freeze=1))

		self.tagsStatusWindow = self.new_Frame(self.filterTagsWindow, bg=self.col['disp tags win'], width=res.sx(127), height=res.sy(40),
															geom=self.set_geom(row=1, column=2, freeze=1))

		self.tagsStatusLabel = self.new_Label(self.tagsStatusWindow, bg=self.col['disp tags bg'], width=res.sx(7), font=('arial', res.sy(19)),
														  geom=self.set_geom(row=0, column=0, padx=res.sx(1), pady=res.sy(1), ipadx=res.sx(7), ipady=res.sy(2)))


		self.showFilterInfoWindow = self.new_Frame(self.filterWindow, bg=self.col['filterwin'], width=res.sx(740), height=res.sy(300),
																 geom=self.set_geom(row=1, column=1, sticky=S, columnspan=2, freeze=1))
		self.showFilterInfoFrame = self.new_Frame(self.showFilterInfoWindow, bg='#000000', width=res.sx(730), height=res.sy(290),
																geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5), freeze=1))


		self.filterInfoTitle = self.new_Label(self.showFilterInfoFrame, text='', bg='#000000', font=('times', res.sy(36)), width=res.sx(20), anchor=W,
														  geom=self.set_geom(row=0, column=0, padx=res.sx(10), pady=res.sy(10), ipadx=res.sx(9), sticky=W))

		self.filterWordsFrame = self.new_Frame(self.showFilterInfoFrame, bg='#000000', width=res.sx(565), height=res.sy(200),
															geom=self.set_geom(row=1, column=0, padx=res.sx(10), freeze=1))

		self.filterKanaLabel = self.new_Label(self.filterWordsFrame, bg='#000000', font=('arial', res.sy(20)),
														  geom=self.set_geom(row=0, column=0))

		self.filterEngLabel = self.new_Label(self.filterWordsFrame, bg='#000000', font=('arial', res.sy(20)),
														 geom=self.set_geom(row=0, column=1))

		self.filterTagsFrame = self.new_Frame(self.showFilterInfoFrame, bg='#000000', width=res.sx(135), height=res.sy(200),
														  geom=self.set_geom(row=1, column=1, columnspan=2, sticky=W, freeze=1))

		self.filterTagsLabel = self.new_Label(self.filterTagsFrame, bg='#000000', font=('arial', res.sy(16)), width=res.sx(10),
														  geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5)))

		self.filterGradeLabel = self.new_Label(self.showFilterInfoFrame, bg='#000000', font=('arial', res.sy(36)), width=res.sx(2),
															geom=self.set_geom(row=0, column=1, sticky=W))
		self.filterJlptLabel = self.new_Label(self.showFilterInfoFrame, bg='#000000', font=('arial', res.sy(36)), width=res.sx(2),
														  geom=self.set_geom(row=0, column=2, padx=res.sx(10), sticky=W))






		self.massFilteringWindow = self.new_Frame(self.filterWindow, width=res.sx(340), height=res.sy(465), bg=self.col['filterwin'],
																geom=self.set_geom(row=0, column=2, sticky=N, pady=res.sy(10), rowspan=2, freeze=1))

		self.massFilteringFrame = self.new_Frame(self.massFilteringWindow, width=res.sx(335), height=res.sy(130), bg=self.col['filterbg'],
															  geom=self.set_geom(row=0, column=0, pady=res.sy(5), freeze=1))

		self.groupingModeButton = self.new_Button(self.massFilteringFrame, text='Union', font=('arial', res.sy(14)), width=res.sx(9),
																command=self.toggle_grouping_mode,
																geom=self.set_geom(row=1, column=0, padx=res.sx(10), pady=res.sy(40), rowspan=2),
																state=DISABLED)

		self.incAllButton = self.new_Button(self.massFilteringFrame, text='Inc All', font=('arial', res.sy(14)), width=res.sx(6), 
															 bg=self.col['all bg'], fg=self.col['inc fg'],
															 command=lambda: self.adjust_filter('all', 'inc'),
															 geom=self.set_geom(row=1, column=1, pady=res.sy(8)))
		self.excAllButton = self.new_Button(self.massFilteringFrame, text='Exc All', font=('arial', res.sy(14)), width=res.sx(6), 
															 bg=self.col['all bg'], fg=self.col['exc fg'],
															 command=lambda: self.adjust_filter('all', 'exc'),
															 geom=self.set_geom(row=2, column=1))
		self.incShownButton = self.new_Button(self.massFilteringFrame, text='Inc Shown', font=('arial', res.sy(14)), width=res.sx(9), 
															 bg=self.col['shown bg'], fg=self.col['inc fg'],
															 command=lambda: self.adjust_filter('shown', 'inc'),
															 geom=self.set_geom(row=1, column=2, padx=res.sx(10)))
		self.excShownButton = self.new_Button(self.massFilteringFrame, text='Exc Shown', font=('arial', res.sy(14)), width=res.sx(9), 
															 bg=self.col['shown bg'], fg=self.col['exc fg'],
															 command=lambda: self.adjust_filter('shown', 'exc'),
															 geom=self.set_geom(row=2, column=2))

		self.difficultyWindow = self.new_Frame(self.massFilteringWindow, width=res.sx(335), height=res.sy(320), bg=self.col['filterbg'],
															geom=self.set_geom(row=1, column=0, freeze=1))

		self.timerWindow = self.new_Frame(self.difficultyWindow, width=res.sx(255), height=res.sy(46), bg=self.col['timerbg'],
													 geom=self.set_geom(row=0, column=0, freeze=1))
		self.timerFrame = self.new_Frame(self.timerWindow, width=res.sx(166), height=res.sy(40), bg='#000000',
													geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(3), freeze=1))


		#configurable by time
		self.timerLabel = self.new_Label(self.timerFrame, width = 10, font = ('arial', 18), anchor = W, bg = '#000000', fg = '#ffffff',
													geom = self.set_geom(row = 0, column = 0, pady = 4))

		self.addTimeButton = self.new_Button(self.timerWindow, text = '+', font = ('arial', 15), width = 2, bg = '#000000', fg = self.col['timerbg'], 
														 command = lambda: self.configure_time(1),
														 geom = self.set_geom(row = 0, column = 2, padx = 3, ipadx = 2))
		self.takeTimeButton = self.new_Button(self.timerWindow, text = '-', font = ('arial', 15), width = 2, bg = '#000000', fg = self.col['timerbg'], 
														 command = lambda: self.configure_time(-1),
														 geom = self.set_geom(row = 0, column = 1, ipadx = 2))

		self.lifeWindow = self.new_Frame(self.difficultyWindow, width = 255, height = 46, bg = self.col['lifebg'],
													geom = self.set_geom(row = 1, column = 0, freeze = 1))
		self.lifeFrame = self.new_Frame(self.lifeWindow, width = 166, height = 40, bg = '#000000',
												  geom = self.set_geom(row = 0, column = 0, padx = 3, pady = 3, freeze = 1))

		#configurable by lives
		self.lifeLabel = self.new_Label(self.lifeFrame, width = 10, font = ('arial', 18), anchor = W, bg = '#000000', fg = '#ffffff',
												 geom = self.set_geom(row = 0, column = 0, pady = 4))

		self.addLifeButton = self.new_Button(self.lifeWindow, text = '+', font = ('arial', 15), width = 2, bg = '#000000', fg = self.col['lifebg'], 
														 command = lambda: self.configure_life(1),
														 geom = self.set_geom(row = 0, column = 2, padx = 3, ipadx = 2))
		self.takeLifeButton = self.new_Button(self.lifeWindow, text = '-', font = ('arial', 15), width = 2, bg = '#000000', fg = self.col['lifebg'], 
														 command = lambda: self.configure_life(-1),
														 geom = self.set_geom(row = 0, column = 1, ipadx = 2))

		self.recoverWindow = self.new_Frame(self.difficultyWindow, width = 255, height = 90, bg = self.col['recoverbg'],
														geom = self.set_geom(row = 2, column = 0, freeze = 1))
		self.recoverFrame = self.new_Frame(self.recoverWindow, width = 247, height = 40, bg = '#000000',
														geom = self.set_geom(row = 0, column = 0, padx = 3, pady = 3, columnspan = 2, freeze = 1))

				# configurable by recover
		self.recoverLabel = self.new_Label(self.recoverFrame, width=res.sx(12), font=('arial', res.sy(18)), anchor=W, bg='#000000', fg='#ffffff',
													  geom=self.set_geom(row=0, column=0, pady=res.sy(4)))

		self.addRecoverButton = self.new_Button(self.recoverWindow, text='+', font=('arial', res.sy(15)), width=res.sx(2), bg='#000000', fg=self.col['recoverbg'], 
															 command=lambda: self.configure_recover(1),
															 geom=self.set_geom(row=1, column=1, padx=res.sx(3), ipadx=res.sx(2), sticky=E))
		self.takeRecoverButton = self.new_Button(self.recoverWindow, text='-', font=('arial', res.sy(15)), width=res.sx(2), bg='#000000', fg=self.col['recoverbg'], 
															  command=lambda: self.configure_recover(-1),
															  geom=self.set_geom(row=1, column=1, padx=res.sx(42), ipadx=res.sx(2), sticky=E))

		self.languageWindow = self.new_Frame(self.difficultyWindow, width=res.sx(255), height=res.sy(65), bg=self.col['inactive language fg'],
														geom=self.set_geom(row=3, column=0, freeze=1))
		self.languageFrame = self.new_Frame(self.languageWindow, width=res.sx(247), height=res.sy(59), bg='#000000',
														geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(3), freeze=1))

		self.languageButtons = {
			'jap': self.new_Button(self.languageFrame, text='あ', font=('arial', res.sy(19)), width=res.sx(4), fg=self.col['inactive language fg'], bg=self.col['inactive language bg'], command=lambda: self.select_language('jap'),
																	  geom=self.set_geom(row=0, column=0, padx=res.sx(9), pady=res.sy(5))),
			'eng': self.new_Button(self.languageFrame, text='A', font=('arial', res.sy(19)), width=res.sx(4), fg=self.col['inactive language fg'], bg=self.col['inactive language bg'], command=lambda: self.select_language('eng'),
																	  geom=self.set_geom(row=0, column=1)),
			'both': self.new_Button(self.languageFrame, text='あ/A', font=('arial', res.sy(19)), width=res.sx(4), fg=self.col['inactive language fg'], bg=self.col['inactive language bg'], command=lambda: self.select_language('both'),
																		geom=self.set_geom(row=0, column=2, padx=res.sx(9)))
		}

		self.repetitionWindow = self.new_Frame(self.difficultyWindow, width=res.sx(80), height=res.sy(247), bg=self.col['repetitionbg'],
															geom=self.set_geom(row=0, column=1, rowspan=4, freeze=1))
		self.repetitionFrame = self.new_Frame(self.repetitionWindow, width=res.sx(74), height=res.sy(241), bg='#000000',
														  geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(3), freeze=1))

		# configurable by repetition
		self.repetitionLabel = self.new_Label(self.repetitionFrame, font=('arial', res.sy(11)), width=res.sx(7), fg=self.col['repetitionbg'], bg='#000000',
														  geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(5)))

		# configurable by repetition
		self.repetitionScale = self.new_Scale(self.repetitionFrame, from_=0, to=0, length=res.sy(150), showvalue=0, orient=VERTICAL,
														  command=self.configure_repetition,
														  geom=self.set_geom(row=1, column=0))

		# frame containing button to set configuration to default
		self.presetsFrame = self.new_Frame(self.difficultyWindow, width=res.sx(325), height=res.sy(70), bg=self.col['filterbg'],
													  geom=self.set_geom(row=4, column=0, freeze=1, columnspan=2))

		self.newPresetButton = self.new_Button(self.presetsFrame, text='New preset', font=('arial', res.sy(16)), bg=self.col['new preset bg'], 
															command=lambda: self.open_preset_window(1),
															geom=self.set_geom(row=0, column=0, padx=res.sx(20)))

		self.openPresetsButton = self.new_Button(self.presetsFrame, text='Open presets', font=('arial', res.sy(16)), bg=self.col['open presets bg'], 
															  command=self.open_preset_window, 
															  geom=self.set_geom(row=0, column=1, pady=res.sy(16)))

		# frame containing the play and back buttons
		self.transitionsFrame = self.new_Frame(self.mainWin, width=res.sx(200), height=res.sy(800), bg=self.col['transitionsbg'],
															geom=self.set_geom(row=0, column=2, padx=res.sx(10), sticky=N, freeze=1))

		self.userLabel = self.new_Label(self.transitionsFrame, font=('helvatica', res.sy(20)), bg=self.col['transitionsbg'], fg='#ffffff',
												  geom=self.set_geom(row=0, column=0, pady=res.sy(10)))

		# Press this button to start the flashcard game with configured settings
		self.playButton = self.new_Button(self.transitionsFrame, text='Play', font=('arial', res.sy(20)), bg='#0054a8', fg='#ff80ff', width=res.sx(6), 
													 command=lambda: self.execute_transition('play'),
													 geom=self.set_geom(row=1, column=0, padx=res.sx(50), pady=res.sy(20)))
		self.backButton = self.new_Button(self.transitionsFrame, text='Back', font=('arial', res.sy(20)), bg='#0054a8', fg='#ff80ff', width=res.sx(6), 
													 command=lambda: self.execute_transition('main'),
													 geom=self.set_geom(row=2, column=0))


		self.flahscardFg = {}





	def execute_transition(self, destination):
		self.unbind_editable_labels()
		
		if destination == 'main':
			self.moveto_window(mainMenu)
		elif destination == 'play':
			data = {kanji: self.allFlashcards[kanji][0] for kanji in self.filterLabels if self.filterLabels[kanji].status in ('normal', 'inverted')}
			self.moveto_window(gameInterface)
			gameInterface.start_new_game(data, gamemode = self.gamemode, 
														  difficulties = self.settings, 
														  language = self.settings['language'],
														  showkana = self.toggleKana,
														  invoke_exit = self.return_to_settings)

		self.clear_hover_widgets()

	def return_to_settings(self, gameinterface):
		gameinterface.moveto_window(gameSettings)
		self.load_defaults()

	def clear_hover_widgets(self):
		for tag in self.tagsDisplays:
			self.tagsDisplays[tag].destroy()
		del self.tagsDisplays
		for kanji in self.filterLabels:
			self.filterLabels[kanji].label.destroy()

	def load_defaults(self):
		#single variable settings
		self.settings = {}
		self.settings['user'] = AccountsInterface.loggedInUser
		self.userPresets = cfg.get_user_settings(self.settings['user'])
		self.activePreset = cfg.get_default_settings(self.userPresets)

		self.activePreset['tags'] = [inverse_supercode(tag) for tag in self.activePreset['tags']]

		#multi variable settings
		self.allFlashcards = libraryInterface.allData

		self.groupingMode = 'union'
		self.toggleKana = False
		self.showKanaButton.config(text = f"'Show Kana:\n{'Yes' if self.toggleKana is True else 'No'}")

		self.set_filters()
		self.set_settings()

		self.select_language(self.settings['language'])

		self.gamemode = DEFAULT_GAME_MODE	
		self.set_game_mode(self.gamemode)

		#binding time / live / recover labels

		self.bind_editable_labels()


	def bind_editable_labels(self):
		self.timerLabel.bind('<Button-1>', lambda _: self.select_editable_label(self.timerLabel))
		self.lifeLabel.bind('<Button-1>', lambda _: self.select_editable_label(self.lifeLabel))
		self.recoverLabel.bind('<Button-1>', lambda _: self.select_editable_label(self.recoverLabel))

		self.activeLabel = None
		self.initialValue = 0

	def unbind_editable_labels(self):
		self.timerLabel.unbind('<Button-1>')
		self.lifeLabel.unbind('<Button-1>')
		self.recoverLabel.unbind('<Button-1>')

		self.deactivate_active_label()

		del self.activeLabel
		del self.initialValue

	def select_editable_label(self, label):
		text = label.cget('text')
		value = text[text.index(':') + 2:]

		if label != self.activeLabel:
			self.deactivate_active_label()
			self.activate_editable_label(label, value, text)

	def deactivate_active_label(self):
		if self.activeLabel != None:
			self.deactivate_editable_label(self.activeLabel, change = False)

	def activate_editable_label(self, label, value, text):
		label.config(text = text[:text.index(value)], fg = '#ffff00')
		for num in range(10):
			keystring = f'<KeyPress-{num}>'
			self.root.bind(keystring, self.edit_editable_label)

		self.activeLabel = label
		self.initialValue = value

		self.root.bind('<Return>', lambda e, label = label, change = True: self.deactivate_editable_label(label, change))
		self.root.bind('<Escape>', lambda e, label = label, change = False: self.deactivate_editable_label(label, change))

	def deactivate_editable_label(self, label, change):
		currentText = label.cget('text')
		label.config(text = f"{currentText[:currentText.index(':') + 1]} {self.initialValue}" if (change is False) else currentText, fg = '#ffffff')

		settingKey = {'T': 'time', 'L': 'lives', 'R': 'recover'}[currentText[0]]
		if change is False:
			self.settings[settingKey] = int(self.initialValue)

		for num in range(10):
			keystring = f'<KeyPress-{num}>'
			self.root.unbind(keystring)

		self.root.unbind('<Return>')
		self.root.unbind('<Escape>')

		self.activeLabel = None
		self.initialValue = 0
		
	def edit_editable_label(self, event):
		digit = event.char
		currentText = self.activeLabel.cget('text')
		currentText += '' if (digit == '0') and (currentText[-1] == ' ') else digit
		try:
			resultValue = int(currentText[::-1][:currentText[::-1].index(':') - 1][::-1])
		except ValueError:
			resultValue = 0

		settingKey = {'T': 'time', 'L': 'lives', 'R': 'recover'}[currentText[0]]

		if resultValue < 999:
			self.activeLabel.config(text = currentText)
			self.settings[settingKey] = int(resultValue)

		else:
			textWithoutNumber = currentText[:currentText.index(':') + 1]
			self.activeLabel.config(text = f'{textWithoutNumber} 999')
			self.settings[settingKey] = 999
			self.deactivate_editable_label(label = self.activeLabel, change = True)








	def set_game_mode(self, gamemode):
		#changes the gamemode the user wants to play. currently supports 'vocab' and 'writing' gamemodes.
		self.gamemode = gamemode
		self.gamemodeTitle.config(text = gamemode)

	def writing_toggle_showing_kana(self):
		if self.toggleKana is True:
			self.showKanaButton.config(text = 'Show Kana:\nNo')
			self.toggleKana = False
		else:
			self.showKanaButton.config(text = 'Show Kana:\nYes')
			self.toggleKana = True

	def set_filters(self):

		self.filtersList = []
		self.swapsList = [mainMenu.kanjiData['kanji'][int(num) - 1] for num in self.activePreset['swap']]
		self.logicsDict = {'grade': self.activePreset['gradelogic'],
								 'jlpt': self.activePreset['jlptlogic'],
								 'length': self.activePreset['lengthlogic'],
								 'tags': self.activePreset['tagslogic']}

		#default logic buttons
		for logic, button in zip(('gradelogic', 'jlptlogic', 'lengthlogic', 'tagslogic'), (self.gradeLogicButton, self.jlptLogicButton, self.lengthLogicButton, self.tagsLogicButton)):

			button.config(text = f'Logic: {"OR" if self.activePreset[logic] == "or" else "AND"}',
							  bg = self.col['or logicbg'] if self.activePreset[logic] == 'or' else self.col['and logicbg'],
							  command = lambda type_ = logic[:logic.index('logic')] ,logic = logic: self.configure_logic(type_, self.activePreset[logic]))

		try:
			defaultButtons = {'grades': self.gradeButtons, 'jlpt': self.jlptButtons, 'length': self.lengthButtons}
			activeColours = {'grades': self.col['active grade'], 'jlpt': self.col['active jlpt'], 'length': self.col['active length']}
		except KeyError:
			pass

		#setting default grade, jlpt and length buttons
		for type_, extension in zip(('grades', 'jlpt', 'length', 'tags'), ('G', 'J', 'L', 'T_')):

			for key in self.activePreset[type_]:

				try:
					defaultButtons[type_][key].config(fg = self.col['highlightfg'], bg = activeColours[type_])

				except KeyError:
					pass

				filterKey = extension + key
				self.filtersList.append(filterKey)

		self.filterLabels = {}
		for kanji in self.allFlashcards:
			info = self.allFlashcards[kanji]

			grade = 'G' + info[1]
			jlpt = 'J' + info[2]
			tags = ['T_' + tag for tag in info[3]]

			self.filterLabels[kanji] = filter_label(kanji, info[0], self.viewFiltersFrame,
																 grade = grade,
																 jlpt = jlpt,
																 tags = tags,
																 filters = self.filtersList,
																 swaps = self.swapsList,
																 logics = self.logicsDict,
																 dispWidgets = {'kanji': self.filterInfoTitle,
																					 'kana': self.filterKanaLabel,
																					 'eng': self.filterEngLabel,
																					 'grade': self.filterGradeLabel,
																					 'jlpt': self.filterJlptLabel,
																					 'tags': self.filterTagsLabel},
																 mode = self.groupingMode)

		def display_tag_name(event, tag, col, enter):

			if enter == 1:
				rgb = tuple([int(col[1:][2*i:2*(i+1)], 16) for i in range(3)])
				brighten = [2*primaryColour + (255 - primaryColour) // 4 if primaryColour < 109 else 255 for primaryColour in rgb]
				self.tagsStatusLabel.config(text = tag[2:], fg = f'#{brighten[0]:02x}{brighten[1]:02x}{brighten[2]:02x}')

			else:
				self.tagsStatusLabel.config(text = '')

		defaultTagsDisplay = []
		self.tagsDisplays = {'T_' + tag[0]: Frame(self.displayTagsFrame, width = res.sx(10), height = res.sy(10), bg = tag[1]) for tag in mainMenu.tagsList}

		for num, tag in enumerate(self.tagsDisplays):
			self.tagsDisplays[tag].bind('<Enter>', lambda e, tag = tag, col = mainMenu.tagsList[num][1]: display_tag_name(e, tag, col, 1))
			self.tagsDisplays[tag].bind('<Leave>', lambda e, tag = tag, col = mainMenu.tagsList[num][1]: display_tag_name(e, tag, col, 0))

			if tag in [key for key in self.filtersList if key[0] == 'T']:
				defaultTagsDisplay.append(mainMenu.tagsList[num])

		self.update_tag_filter(defaultTagsDisplay)
		self.adjust_filter('init', '')

	def set_settings(self):
		self.settings['time'] = int(self.activePreset['time'])
		self.settings['lives'] = int(self.activePreset['lives'])
		self.settings['recover'] = int(self.activePreset['recover'])
		self.settings['language'] = self.activePreset['language']
		self.settings['repetition'] = int(self.activePreset['repetition'])

		self.timerLabel.config(text = f"Time (s): {self.settings['time']}")
		self.lifeLabel.config(text = f"Lives: {self.settings['lives']}")
		self.recoverLabel.config(text = f"Recover (s): {self.settings['recover']}")

	def configure_time(self, time):
		self.settings['time'] += time if (self.settings['time'] > 1) else (0 if time == -1 else 1)
		self.timerLabel.config(text = f"Time (s): {self.settings['time']}")

	def configure_life(self, life):
		self.settings['lives'] += life if (self.settings['lives'] > 1) else (0 if life == -1 else 1)
		self.lifeLabel.config(text = f"Lives: {self.settings['lives']}")

	def configure_recover(self, time):
		self.settings['recover'] += time if (self.settings['recover'] > 1) else (0 if time == -1 else 1)
		self.recoverLabel.config(text = f"Recover (s): {self.settings['recover']}")

	def select_language(self, lg):
		self.languageButtons[self.settings['language']].config(bg = self.col['inactive language bg'], fg = self.col['inactive language fg'])
		self.settings['language'] = lg
		self.languageButtons[self.settings['language']].config(bg = self.col['active language bg'], fg = self.col['active language fg'])

	def configure_repetition(self, *args):
		allStatus = [self.filterLabels[kanji].status for kanji in self.filterLabels]
		self.trueTotal = allStatus.count('normal') + allStatus.count('inverted')

		if self.repetitionScale.get() > self.trueTotal:
			self.repetitionScale.set(self.trueTotal)

		self.settings['repetition'] = self.repetitionScale.get()
		self.repetitionLabel.config(text = f"Repetition\n{self.trueTotal - self.settings['repetition']}")

	def adjust_filter(self, type_ = '', infoKey = ''):
		if type_ in ('grade', 'jlpt', 'length'):

			activeBg = {'grade': self.col['active grade'], 'jlpt': self.col['active jlpt'], 'length': self.col['active length']}[type_]
			inactiveBg = {'grade': self.col['inactive grade'], 'jlpt': self.col['inactive jlpt'], 'length': self.col['inactive length']}[type_]
			buttons = {'grade': self.gradeButtons, 'jlpt': self.jlptButtons, 'length': self.lengthButtons}[type_]
			extension = {'grade': 'G', 'jlpt': 'J', 'length': 'L', 'tags': 'T_'}
			key = extension[type_] + infoKey

			if key not in self.filtersList:
				self.filtersList.append(key)
				buttons[infoKey].config(bg = activeBg, fg = self.col['highlightfg'])

			else:
				self.filtersList.remove(key)
				buttons[infoKey].config(bg = inactiveBg, fg = self.col['labelfg'])

		#status: normal, inverted, dim, hidden, pending (reminder: pending is achieved by removing from swaps while in inverted state.)
		#list of filters applied: self.filtersList
		#all kanji status: self.filterLabels

		elif type_ == 'shown' and infoKey == 'inc':

			#possible paths:
			#normal -> normal
			#inverted -> inverted
			#darkened -> normal (REMOVE FROM SWAP)
			#pending -> inverted (ADD TO SWAP)

			for kanji in self.filterLabels:
				status = self.filterLabels[kanji].status

				if status == 'darkened':
					self.swapsList.remove(kanji)

				elif status == 'pending':
					self.swapsList.append(kanji)


		elif type_ == 'shown' and infoKey == 'exc':

			#possible paths:
			#normal -> darkened (ADD TO SWAP)
			#inverted - > pending (REMOVE FROM SWAP)
			#darkened - > darkened
			#pending -> pending

			for kanji in self.filterLabels:
				status = self.filterLabels[kanji].status

				if status == 'normal':
					self.swapsList.append(kanji)

				elif status == 'inverted': # <--- see if it's possible to get kanji to assume 'dim' status
					self.swapsList.remove(kanji)


		elif type_ == 'all' and infoKey == 'inc':
			print('wip')

			#possible paths:
			#normal -> normal
			#inverted -> inverted
			#dim -> normal (REMOVE FROM SWAP)
			#hidden -> inverted (ADD TO SWAP)
			#pending -> inverted (ADD TO SWAP)

		elif type_ == 'all' and infoKey == 'inc':
			print('wip')

			#possible paths:

			#possible paths:
			#normal -> hidden # (EMPTY FILTERS)
			#inverted - > hidden (REMOVE FROM SWAP, EMPTY FILTERS)
			#dim - > hidden (REMOVE FROM SWAP)
			#hidden -> hidden
			#pending -> #hidden

		elif type_ in ('shown', 'all'):
			print('owo')

		tags = [tag for tag in self.filtersList if tag[0] == 'T']

		logics = {'and': [key for key in self.logicsDict if self.logicsDict[key] == 'and'], 
					 'or': [key for key in self.logicsDict if self.logicsDict[key] == 'or']}

		jumps = []
		for kanji in self.filterLabels:
			obj = self.filterLabels[kanji]
			statusBeforeUpdate = obj.status

			obj.label.config(fg = obj.get_status(self.filtersList, tagsList = tags, logic = logics, swaps = self.swapsList, mode = self.groupingMode))

			#reduced filters list
			if statusBeforeUpdate in ('normal', 'inverted', 'darkened', 'pending') and obj.status in ('hidden', 'pending'):
				obj.label.grid_forget()

			#elongated filters list
			elif statusBeforeUpdate in ('pending', 'hidden') and obj.status in ('nomrmal', 'inverted', 'darkened'):
				pass

			elif statusBeforeUpdate in ('normal', 'inverted', 'darkened') and obj.status in ('normal', 'inverted', 'darkened'):
				jumps.append(kanji)

		total = len(self.filterLabels)
		allStatus = [self.filterLabels[kanji].status for kanji in self.filterLabels]
		dispTotal = total - allStatus.count('hidden') - allStatus.count('pending')

		counter = 0
		wantedColumns = 4
		remainder = dispTotal % wantedColumns

		for kanji in self.filterLabels:
			obj = self.filterLabels[kanji]

			if not obj.status in ('hidden', 'pending'):
				obj.get_coords(counter, dispTotal, wantedColumns, remainder, (kanji in jumps))
				counter += 1

		self.trueTotal = dispTotal - allStatus.count('darkened')

		self.filterTotalLabel.config(text = f" Total: {self.trueTotal} / {mainMenu.kanjiData['size']}")
		self.repetitionScale.config(to = self.trueTotal)
		self.repetitionLabel.config(text = f"Repetition\n{self.trueTotal - self.repetitionScale.get()}")
		self.viewFiltersFrame.resizeScrollWindow()

	def clear_filter_buttons(self):
		for buttons, bgKey in zip((self.gradeButtons, self.jlptButtons, self.lengthButtons), ('grade', 'jlpt', 'length')):
			for key in buttons:
				buttons[key].config(bg = self.col[f"inactive {bgKey}"], fg = self.col['labelfg'])

	def toggle_grouping_mode(self):
		if self.groupingMode == 'union':
			self.groupingMode = 'intersection'

		elif self.groupingMode == 'intersection':
			self.groupingMode = 'union'

		self.groupingModeButton.config(text = self.groupingMode.capitalize())
		self.adjust_filter()

	def update_tag_filter(self, *args):

		self.displayTagsFrame.grid_propagate(0)

		tagsList = {pair[0]: pair[1] for pair in args[0]}
		newDefault = []
		counter = 0
		for pair in mainMenu.tagsList:

			row = counter // 12
			column = counter % 12

			tagFilter = 'T_' + pair[0]

			if (tagFilter in self.filtersList) and not (pair[0] in tagsList):
				self.filtersList.remove(tagFilter)
				self.tagsDisplays[tagFilter].grid_forget()

			elif (pair[0] in tagsList) and not (tagFilter in self.filtersList):
				self.filtersList.append(tagFilter)
				newDefault.append(pair[0])
				self.tagsDisplays[tagFilter].grid(row = row, column = column, padx = res.sx(4), pady = res.sy(4))
				counter += 1

			elif (pair[0] in tagsList) and (tagFilter in self.filtersList):
				newDefault.append(pair[0])
				self.tagsDisplays[tagFilter].grid_configure(row = row, column = column, padx = res.sx(4), pady = res.sy(4))
				counter += 1

		self.filterTagsButton.config(command = lambda: open_tags_window(mainMenu.tagsList, bg = '#0d0613',
																							 invoke = self.update_tag_filter,
																							 default = newDefault))

		if tagsList == {}:
			self.tagsStatusLabel.config(text = 'No Tags', fg = '#5a5a5a')

		else:
			self.tagsStatusLabel.config(text = '')

		self.adjust_filter('tags', '')

	def configure_logic(self, type_, logic):
		directory = {'grade': self.gradeLogicButton, 'jlpt': self.jlptLogicButton, 'length': self.lengthLogicButton, 'tags': self.tagsLogicButton}
		directory[type_].config(text = f'Logic: {"AND" if logic == "or" else "OR"}',
										bg = self.col['and logicbg'] if logic == 'or' else self.col['or logicbg'],
										command = lambda: self.configure_logic(type_, 'and' if logic == 'or' else 'or'))

		self.logicsDict[type_] = 'and' if logic == 'or' else 'or'
		self.adjust_filter('logic', '')

	def open_preset_window(self, *args):
		currentSettings = self.get_all_active_settings()
		self.presetWindow = client.open_preset_window(user = self.settings['user'],
																	 presets = self.userPresets,
																	 currentPreset = self.activePreset,
																	 new = ((1) in args),
																	 activeSet = currentSettings,
																	 exit = self.update_presets if ((1) in args) else self.set_preset,
																	 updateConfig = cfg.set_default_preset,
																	 updateValues = cfg.overwrite_preset_values,
																	 newPreset = cfg.append_new_preset)

	def set_preset(self, *args):
		self.activePreset = args[1]
		self.select_language(self.activePreset['language'])

		self.clear_hover_widgets()
		self.clear_filter_buttons()

		self.set_filters()
		self.set_settings()

	def update_presets(self):
		self.userPresets = cfg.get_user_settings(self.settings['user'])

	def get_all_active_settings(self):
		defaultGrades = ','.join([grade[1:] for grade in self.filtersList if grade[0] == 'G'])
		defaultJlpt = ','.join([jlpt[1:] for jlpt in self.filtersList if jlpt[0] == 'J'])
		defaultLength = ','.join([length[1:] for length in self.filtersList if length[0] == 'L'])
		defaultTags = ','.join([supercode(tag[2:]) for tag in self.filtersList if tag[0:2] == 'T_'])
		defaultSwaps = ','.join([str(num) for num in sorted([mainMenu.kanjiData['kanji'].index(kanji) + 1 for kanji in self.swapsList])])
		settingsDict = {
							'grades': defaultGrades if defaultGrades != '' else 'none',
							'gradelogic': self.logicsDict['grade'],
							'jlpt': defaultJlpt if defaultJlpt != '' else 'none',
							'jlptlogic': self.logicsDict['jlpt'],
							'length': defaultLength if defaultLength != '' else 'none',
							'lengthlogic': self.logicsDict['length'],
							'tags': defaultTags if defaultTags != '' else 'none',
							'tagslogic': self.logicsDict['tags'], 
							'swap': defaultSwaps if defaultSwaps != '' else 'none',
							'time': self.settings['time'],
							'lives': self.settings['lives'],
							'recover': self.settings['recover'],
							'language': self.settings['language'],
							'repetition': self.settings['repetition']
							}

		return settingsDict

gameSettings = gameSettings_interface(root, bg = '#000000')

class filter_label(gameSettings_interface):

	engSizes = get_char_pixels(res.sy(20))
	engsWidth = res.sx(493)

	def __init__(self, kanji, words, viewer, grade, jlpt, tags, filters, swaps, logics, dispWidgets, mode):

		self.kanji = kanji
		self.words = words

		self.grade = grade
		self.jlpt = jlpt
		self.length = f"L{len(self.kanji)}" if len(self.kanji) < 4 else "L4+"
		self.tags = tags

		self.litFg = {1: '#ffffff', 2: '#00ff00', 3: '#00ffff', 4: '#b266ff'}[len(self.kanji)]
		self.dimFg = {1: '#4d4d4d', 2: '#008000', 3: '#007f80', 4: '#4c0099'}[len(self.kanji)]

		self.viewer = viewer.canvasFrame
		self.dispWidgets = dispWidgets

		logicFilters = {'and': [key for key in logics if logics[key] == 'and'],
							 'or': [key for key in logics if logics[key] == 'or']}

		kanas, engs = [kana for kana in words], [words[kana] for kana in words]

		self.kanaText = format_kana(kanas, width = res.sx(4))
		self.engText = format_english(engs, pixels = filter_label.engSizes, maxWidth = res.sx(filter_label.engsWidth))

		tagsList = [tag for tag in filters if tag[0] == 'T']
		self.tagsText = ''.join([tag[2:] + ('\n' if num != len(tags) else '') for (num, tag) in enumerate(tags, start = 1)])
		self.label = Label(self.viewer, text = self.kanji[0], font = ('times', res.sy(28)),
								 bg = '#000000', fg = self.get_status(filters, tagsList, logicFilters, swaps, mode = mode))

		self.label.bind('<Enter>', lambda _: self.highlight(1))
		self.label.bind('<Leave>', lambda _: self.highlight(0))
		self.label.bind('<Button-1>', self.swap)

	def get_status(self, filters, tagsList, logic, swaps, mode):
		filtertypes = [Type[0] for Type in filters]

		if tagsList == []: #ignore tags
			tagsSatisfied = None

		elif tagsList != [] and self.tags == []:
			tagsSatisfied = False

		else:
			tagsSatisfied = (True in [(tag in tagsList) for tag in self.tags])

		logicKeys = {
						'grade': self.grade in filters if ('G' in filtertypes) else None,
						'jlpt': self.jlpt in filters if ('J' in filtertypes) else None,
						'length': self.length in filters if ('L' in filtertypes) else None,
						'tags': tagsSatisfied
						}

		checkOr = [logicKeys[key] for key in logic['or'] if logicKeys[key] != None]
		checkAnd = [logicKeys[key] for key in logic['and'] if logicKeys[key] != None]

		andSatisfied = not (False in checkAnd) if (len(checkAnd) > 0) else False
		orSatistfied = True in checkOr

		Filter = (andSatisfied or orSatistfied) if (mode == 'union') else (andSatisfied and orSatistfied)
		Swap = self.kanji in swaps

		if Filter and not Swap:
			self.status = 'normal'

		elif Filter and Swap:
			self.status = 'darkened'

		elif not Filter and Swap:
			self.status = 'inverted'

		else:
			self.status = 'hidden'

		#special status: "pending"
		#only applies if the status is 'inverted' and is manually removed from swaps. if this happens, the label will acquire the 'pending' status.
		#in this status, if filters is adjusted such that this label is present in filters, change status to 'normal'. otherwise, change it to 'hidden'.
		#display style of 'pending' status is the same as 'darkened'.

		self.highlightFg = '#ffff00' if self.status in ('normal', 'inverted') else '#ff0000'

		self.currentFg = {'normal': self.litFg, 'inverted': self.litFg, 'darkened': self.dimFg, 'hidden': self.litFg}[self.status]
		return self.currentFg

	def get_coords(self, count, total, wantedColumns, remainder, repositioning):
		rows = (total // wantedColumns) + (1 if remainder != 0 else 0)
		row = count % rows
		column = wantedColumns - count // rows

		if repositioning:
			self.label.grid_configure(row = row, column = column, ipadx = res.sx(3), ipady = res.sy(3))

		else:
			self.label.grid(row = row, column = column, ipadx = res.sx(3), ipady = res.sy(3))

	def highlight(self, num):

		self.label.config(fg = self.highlightFg if num == 1 else self.currentFg,
								font = ('arial', res.sy(28), 'bold') if num == 1 else ('times', res.sy(28)))

		padding = 2 if num == 1 else 3
		self.label.grid_configure(ipadx = padding, ipady = padding)

		for key in self.dispWidgets:
			self.dispWidgets[key].config(fg = self.highlightFg)

		self.dispWidgets['kanji'].config(text = self.kanji if num == 1 else '')
		self.dispWidgets['kana'].config(text = self.kanaText if num == 1 else '', justify = 'right', anchor = 'e')
		self.dispWidgets['eng'].config(text = self.engText if num == 1 else '', justify = 'left', anchor = 'w')
		self.dispWidgets['grade'].config(text = self.grade[1:] if num == 1 else '')
		self.dispWidgets['jlpt'].config(text = self.jlpt[1:] if num == 1 else '')
		self.dispWidgets['tags'].config(text = self.tagsText if num == 1 else '')

	def swap(self, *args):
		swapsList = gameSettings.swapsList

		if self.kanji in swapsList:
			swapsList.remove(self.kanji)

		else:
			swapsList.append(self.kanji)

		self.status = {
							'normal': 'darkened', 
							'darkened': 'normal', 
							'inverted': 'pending', #pending - visual: treated as darkened, presence: treated as hidden
							'pending': 'inverted'
							}[self.status]

		signNum = 1 if self.status in ('normal', 'inverted') else -1

		self.highlightFg = '#ffff00' if (self.status in ('normal', 'inverted')) else '#ff0000'
		self.currentFg = self.litFg if (self.status in ('normal', 'inverted')) else self.dimFg

		self.label.config(fg = self.highlightFg)
		for key in self.dispWidgets:
			self.dispWidgets[key].config(fg = self.highlightFg)

		gameSettings.trueTotal += signNum
		gameSettings.filterTotalLabel.config(text = f" Total: {gameSettings.trueTotal} / {mainMenu.kanjiData['size']}")
		gameSettings.repetitionScale.config(to = gameSettings.trueTotal)
		gameSettings.repetitionLabel.config(text = f"Repetition\n{gameSettings.trueTotal - gameSettings.repetitionScale.get()}")
		gameSettings.viewFiltersFrame.resizeScrollWindow()

	# def process_logic(self, grade, jlpt, length, tags, orlogic, andlogic):
	# 	if len(orlogic) == 4:
	# 		return (True or grade or jlpt or length or tags)

	# 	elif len(orlogic) == 3 and 'grade' in andlogic:
	# 		return (True and grade or jlpt or length or tags)

	# 	elif len(orlogic) == 3 and 'jlpt' in andlogic:
	# 		return (True or grade and jlpt or length or tags)

	# 	elif len(orlogic) == 2 and 'grade' in andlogic and 'jlpt' in andlogic:
	# 		return (True and grade and jlpt or length or tags)

	# 	elif len(orlogic) == 3 and 'length' in andlogic:
	# 		return (True or grade or jlpt and length or tags)

	# 	elif len(orlogic) == 2 and 'grade' in andlogic and 'length' in andlogic:
	# 		return (True and grade or jlpt and length or tags)

	# 	elif len(orlogic) == 2 and 'jlpt' in andlogic and 'length' in andlogic:
	# 		return (True or grade and jlpt and length or tags)

	# 	elif len(andlogic) == 3 and 'tags' in orlogic:
	# 		return (True and grade and jlpt and length or tags)

class History:

	def __init__(self, language, kanji, answers, status, pos, win):

		self.language = language
		self.kanji = kanji
		self.answers = answers
		self.status = status
		self.pos = pos
		self.win = win

		self.credit = {0: 'none', 1: 'partial', 2: 'full'}[self.status.count(1)] if self.language == 'both' else {0: 'none', 1: 'full'}[self.status]

		recordBg = {'none': '#ff9999', 'partial': '#ffff99', 'full': '#99ff99'}[self.credit]
		recordFg = {'none': '#800000', 'partial': '#808000', 'full': '#008000'}[self.credit]

		self.recordFrame = Frame(self.win, width=res.sx(350), height=res.sy(200), bg=recordBg)
		self.statusFrame = Frame(self.recordFrame, bg=recordBg)
		self.kanjiLabel = Label(self.recordFrame, text=f"{self.pos}: {self.kanji}", font=('helvatica', res.sy(26)), bg=recordBg, fg=recordFg)

		if self.language in ('jap', 'eng'):
			creditText = u'\u2b55' if self.status == 1 else u'\u274c'
			self.status = Label(self.statusFrame, text=creditText, font=('helvatica', res.sy(30)), bg=recordBg, fg=recordFg, width=res.sx(2))
		else:
			# 2b55: '⭕️', 274c: '❌'
			kanaCreditText = u'\u2b55' if self.status[0] == 1 else u'\u274c'
			engCreditText = u'\u2b55' if self.status[1] == 1 else u'\u274c'
			self.kanaStatus = Label(self.statusFrame, text=kanaCreditText, font=('helvatica', res.sy(30)), bg=recordBg, fg=recordFg, width=res.sx(2))
			self.engStatus = Label(self.statusFrame, text=engCreditText, font=('helvatica', res.sy(30)), bg=recordBg, fg=recordFg, width=res.sx(2))

		self.answersFrame = Frame(self.recordFrame, width=res.sx(350), height=res.sy(120), bg=recordBg)
		answerText = ''
		for kana in self.answers:
			engtext = ', '.join(self.answers[kana])
			answerText += f"{kana}: {engtext}\n"
		answerText = answerText.rstrip('\n')

		self.answersLabel = Label(self.answersFrame, text=answerText, font=('helvatica', res.sy(18)), bg=recordBg, fg=recordFg,
										  anchor=W, justify=LEFT)

	def display(self, num):
		self.recordFrame.grid_propagate(0)
		self.answersFrame.grid_propagate(0)

		self.kanjiLabel.grid(row=0, column=0, padx=res.sx(3), sticky=W)
		self.answersLabel.grid(row=0, column=0, padx=res.sx(5), pady=res.sy(10))
		self.answersFrame.grid(row=1, column=0, columnspan=2)

		if self.language == 'both':
			self.kanaStatus.grid(row=0, column=0, padx=res.sx(5), pady=res.sy(5))
			self.engStatus.grid(row=0, column=1)
		else:
			self.status.grid(row=0, column=0, padx=res.sx(5), pady=res.sy(5))

		self.statusFrame.grid(row=0, column=1, padx=res.sx(3), pady=res.sy(3), sticky=E)
		self.recordFrame.grid(row=num, column=0, padx=res.sx(5), pady=res.sy(5))


class Accounts(client.Window):

	def __init__(self, root, **kwargs):

		super().__init__(root, **kwargs)

		self.col['frames bg'] = '#450000'
		self.col['normal fg'] = '#e0b8b8'

		self.userTitleLabel = self.new_Label(
			self.mainWin,
			font=('times', res.sy(32)),
			text='Users Hub',
			width=res.sx(10),
			bg=self.col['frames bg'],
			fg=self.col['normal fg'],
			geom=self.set_geom(manager='pack', padx=res.sx(10), pady=res.sy(10))
		)

		self.usersListFrame = self.new_Frame(
			self.mainWin,
			width=res.sx(300),
			height=res.sy(600),
			bg=self.col['frames bg'],
			geom=self.set_geom(manager='pack', padx=res.sx(10), freeze=1)
		)

		self.loggedinFrame = self.new_Frame(
			self.usersListFrame,
			bg=self.col['frames bg'],
			geom=self.set_geom(manager='pack', padx=res.sx(10), pady=res.sy(10), hidden=1)
		)

		self.loggedInTitle = self.new_Label(
			self.loggedinFrame,
			font=('times', res.sy(18)),
			bg=self.col['frames bg'],
			fg=self.col['normal fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(10), pady=res.sy(10))
		)

		self.logoutButton = self.new_Button(
			self.loggedinFrame,
			text='Logout',
			font=('times', res.sy(14)),
			width=res.sx(7),
			bg=self.col['normal fg'],
			fg='#000000',
			command=self.logout,
			geom=self.set_geom(row=0, column=1)
		)

		self.setDefaultButton = self.new_Button(
			self.loggedinFrame,
			text='Set default',
			font=('times', res.sy(14)),
			width=res.sx(8),
			bg=self.col['normal fg'],
			fg='#000000',
			command=self.set_default_user,
			geom=self.set_geom(row=1, column=0)
		)

		self.userInputFrame = self.new_Frame(
			self.usersListFrame,
			bg=self.col['frames bg'],
			geom=self.set_geom(manager='pack', padx=res.sx(10), pady=res.sy(10), hidden=1)
		)

		self.userInputTitle = self.new_Label(
			self.userInputFrame,
			text='Username:',
			font=('times', res.sy(18)),
			bg=self.col['frames bg'],
			fg=self.col['normal fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(8), pady=res.sy(10))
		)

		self.userInputEntry = self.new_Entry(
			self.userInputFrame,
			font=('times', res.sy(18)),
			width=res.sx(12),
			justify='left',
			geom=self.set_geom(row=0, column=1, padx=res.sx(10))
		)

		self.loginButton = self.new_Button(
			self.userInputFrame,
			text='Login',
			font=('times', res.sy(14)),
			width=res.sx(7),
			bg=self.col['normal fg'],
			fg='#000000',
			command=lambda: self.login_username(self.get_input(self.userInputEntry)),
			geom=self.set_geom(row=1, column=1)
		)

		self.passwordFrame = self.new_Frame(
			self.usersListFrame,
			bg=self.col['frames bg'],
			geom=self.set_geom(manager='pack', padx=res.sx(10), pady=res.sy(10), hidden=1)
		)

		self.passwordTitle = self.new_Label(
			self.passwordFrame,
			text='Password:',
			font=('times', res.sy(18)),
			bg=self.col['frames bg'],
			fg=self.col['normal fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(8), pady=res.sy(10))
		)

		self.passwordEntry = self.new_Entry(
			self.passwordFrame,
			font=('times', res.sy(18)),
			width=res.sx(12),
			justify='left',
			geom=self.set_geom(row=0, column=1, padx=res.sx(10))
		)

		self.submitPasswordButton = self.new_Button(
			self.passwordFrame,
			text='Submit',
			font=('times', res.sy(14)),
			width=res.sx(6),
			bg=self.col['normal fg'],
			fg='#000000',
			command=lambda: self.login_password(self.get_input(self.passwordEntry)),
			geom=self.set_geom(row=1, column=1)
		)

		self.backFrame = self.new_Frame(
			self.mainWin,
			width=res.sx(300),
			height=res.sy(100),
			bg=self.col['frames bg'],
			geom=self.set_geom(manager='pack', pady=res.sy(10), freeze=1)
		)

		self.backButton = self.new_Button(
			self.backFrame,
			text='Back',
			font=('times', res.sy(20)),
			bg=self.col['normal fg'],
			fg='#000000',
			command=self.back,
			geom=self.set_geom(manager='pack', pady=res.sy(25), ipady=res.sy(8))
		)


		#get all users and their default values
		self.users = users.get_all_users()
		self.defaultUser = self.get_default_user()
		self.loggedInUser = self.get_loggedIn_user(self.defaultUser)

	def back(self):
		self.moveto_window(mainMenu)

	def load_current_user(self):
		#this method is called at the same time the Accounts Window is loaded.
		if self.defaultUser == None:
			self.show_login_page()

		else:
			self.show_user_page(self.loggedInUser)

	def show_login_page(self):
		print('no default user.')
		self.load_widgets(self.userInputFrame)

	def show_user_page(self, defaultUsername):
		self.load_widgets(self.loggedinFrame)
		self.loggedInUser = self.get_loggedIn_user(defaultUsername)

	def login_username(self, name):
		if cfg.verify_username(name):
			self.pendingUsername = name
			self.userInputEntry.delete(0, END)
			self.ask_for_password()

	def ask_for_password(self):
		self.unload_widgets(self.userInputFrame)
		self.load_widgets(self.passwordFrame)
		self.passwordEntry.focus_set()

	def login_password(self, key):
		print('passwords are a WIP.')
		if True: #change this conditional to check if the key is the same as the password.
			self.login(self.pendingUsername)

	def login(self, user):
		self.unload_widgets(self.passwordFrame)
		self.load_widgets(self.loggedinFrame)
		self.loggedInUser = self.get_loggedIn_user(user)
		self.userProfile = cfg.get_user_profile()
		del self.pendingUsername

	def get_default_user(self):
		defaultUser = [user for user in self.users if self.users[user] == '1']
		return None if defaultUser == [] else defaultUser[0]

	def set_default_user(self):
		cfg.overwrite_default_user(self.defaultUser, self.loggedInUser)
		self.defaultUser = self.loggedInUser

	def logout(self):
		self.unload_widgets(self.loggedinFrame)
		self.load_widgets(self.userInputFrame)
		self.userInputEntry.focus_set()

	def get_loggedIn_user(self, username):
		self.loggedInTitle.config(text = f"Logged in as\n{username}")
		return username
		
	def get_input(self, entry):
		userInput = entry.get()
		return userInput

AccountsInterface = Accounts(root, bg = '#300000')

root.mainloop()

print('bai')