from tkinter import *
import translator
import tags
import config as cfg

import resolution as res

#contains the add, remove and edit class windows

class editor:

	def __init__(self, In, width, height):
		self.win = In
		self.width = width
		self.height = height

		self.mainFrame = Frame(self.win, width = self.width, height = self.height)

		self.components = []

	def save(self, widget, row, column, **kwargs):
		geometry = {'row': row, 'column': column, 'padx': kwargs['padx'] if 'padx' in kwargs else 0,
																'pady': kwargs['pady'] if 'pady' in kwargs else 0,
																'ipadx': kwargs['ipadx'] if 'ipadx' in kwargs else 0,
																'ipady': kwargs['ipady'] if 'ipady' in kwargs else 0,
																'sticky': kwargs['sticky'] if 'sticky' in kwargs else None,
																'columnspan': kwargs['columnspan'] if 'columnspan' in kwargs else 1,
																'rowspan': kwargs['rowspan'] if 'rowspan' in kwargs else 1,
																'freeze': kwargs['freeze'] if 'freeze' in kwargs else 1}

		self.components.append((widget, geometry))
		
	def load(self, **kwargs):
		for pair in self.components:
			geom = pair[1]
			pair[0].grid_propagate(geom['freeze'])
			pair[0].grid(row = geom['row'], column = geom['column'], padx = geom['padx'],
																						pady = geom['pady'],
																						ipadx = geom['ipadx'],
																						ipady = geom['ipady'],
																						sticky = geom['sticky'],
																						columnspan = geom['columnspan'],
																						rowspan = geom['rowspan'])

		self.mainFrame.grid(row = 0, column = 0, padx = 5, pady = 5)
		self.mainFrame.grid_propagate(0)

		self.null() if not ('invoke' in kwargs) else kwargs['invoke']()

	def unload(self, *args, **kwargs):
		for pair in self.components:
			pair[0].grid_forget()

		self.mainFrame.grid_forget()
		
		self.null() if not ('invoke' in kwargs) else kwargs['invoke'](*args)

	def null(self, *args, **kwargs):
		#default invoke function, will be called if invoke is not passed into load or unload.
		print('null invoked.')
		return

class adding_editor(editor):
	mainBg = '#bddbbd'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

		self.framesbg = '#041604'
		self.labelsfg = '#e5ffe5'
		self.buttonbg = '#145214'

		self.mainFrame.config(bg = self.mainBg)

		#section for choosing the kanji symbol(s)
		self.addKanjiFrame = Frame(self.mainFrame, bg = self.framesbg)
		self.addKanjiTitle = Label(self.addKanjiFrame, text='New Kanji', font=('arial', res.sy(16)), bg=self.framesbg, fg=self.labelsfg)
		self.kanjiVar = StringVar(name='add new kanji')
		self.kanjiVar.trace_add('write', self.check_kanji_exists)
		self.kanjiEntry = Entry(self.addKanjiFrame, font=('arial', res.sy(24)), width=res.sx(10), justify=CENTER, textvariable=self.kanjiVar)
		self.addKanjiMessage = Label(self.addKanjiFrame, font=('arial', res.sy(16)), bg=self.framesbg, fg=self.labelsfg, anchor='n')

		self.save(self.addKanjiFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2), rowspan=2, sticky='n')
		self.save(self.addKanjiTitle, row=0, column=0, pady=res.sy(5))
		self.save(self.kanjiEntry, row=1, column=0, padx=res.sx(5))
		self.save(self.addKanjiMessage, row=2, column=0, pady=res.sy(10))

		self.addWordsFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.wordsTitle = Label(self.addWordsFrame, text='Kana & English', font=('arial', res.sy(16)), bg=self.framesbg, fg=self.labelsfg)
		self.kanaEntry = Entry(self.addWordsFrame, font=('arial', res.sy(18)), width=res.sx(12), justify=CENTER)
		self.kanaCharButton = Button(self.addWordsFrame, text='あ', font=('times', res.sy(14), 'bold'))
		self.addingTranslator = translator.Translator(self.kanaEntry, ['あ', 'ア'], self.kanaCharButton)

		self.englishEntryFrame = Frame(self.addWordsFrame, bg=self.framesbg)
		self.englishEntries = {num: Entry(self.englishEntryFrame, font=('arial', res.sy(18)), width=res.sx(10), justify=CENTER) for num in range(5)}

		self.pageFrame = Frame(self.addWordsFrame, bg=self.framesbg)
		self.pageLabel = Label(self.pageFrame, text='1', font=('times', res.sy(16)), bg=self.framesbg, fg=self.labelsfg)
		self.pageUpButton = Button(self.pageFrame, text=u'\u25b2', font=('arial', res.sy(8)), width=res.sx(3), command=lambda: self.change_page(-1))
		self.pageDownButton = Button(self.pageFrame, text=u'\u25bc', font=('arial', res.sy(8)), width=res.sx(3), command=lambda: self.change_page(1))

		self.save(self.addWordsFrame, row=0, column=1, pady=res.sy(2), ipady=res.sy(1), rowspan=2)
		self.save(self.wordsTitle, row=0, column=0, pady=res.sy(5), columnspan=2)
		self.save(self.kanaEntry, row=1, column=0, padx=res.sx(5), columnspan=2)
		self.save(self.kanaCharButton, row=2, column=1, pady=res.sy(5))
		self.save(self.englishEntryFrame, row=0, column=2, pady=res.sy(5), rowspan=3)
		for num in self.englishEntries:
			self.save(self.englishEntries[num], row=num, column=0, padx=res.sx(5), pady=res.sy(2))
		self.save(self.pageFrame, row=2, column=0)
		self.save(self.pageLabel, row=0, column=0, padx=res.sx(10), pady=res.sy(10), rowspan=2)
		self.save(self.pageUpButton, row=0, column=1)
		self.save(self.pageDownButton, row=1, column=1)


		# section for choosing grade
		self.chooseGradeFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.gradeTitle = Label(self.chooseGradeFrame, text='Select grade', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.gradeButtonsFrame = Frame(self.chooseGradeFrame, bg=self.framesbg)
		self.chooseGradeButtons = {grade: Button(self.gradeButtonsFrame, text=grade, font=('arial', res.sy(14)), width=res.sx(2),
												bg=self.buttonbg, fg=self.labelsfg, command=lambda grade=grade: self.select_grade(grade))
								for grade in ('1', '2', '3', '4', '5', '6', 'JH', '-')}

		self.save(self.chooseGradeFrame, row=0, column=2, padx=res.sx(2))
		self.save(self.gradeTitle, row=0, column=0, padx=res.sx(5), pady=res.sy(2), sticky='w')
		self.save(self.gradeButtonsFrame, row=1, column=0)
		for num, grade in enumerate(self.chooseGradeButtons):
			self.save(self.chooseGradeButtons[grade], row=0, column=num, padx=res.sx(5), pady=res.sy(5), ipadx=res.sx(3))

		# section for choosing jlpt
		self.chooseJlptFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.jlptTitle = Label(self.chooseJlptFrame, text='Select JLPT', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.jlptButtonsFrame = Frame(self.chooseJlptFrame, bg=self.framesbg)
		self.chooseJlptButtons = {jlpt: Button(self.jlptButtonsFrame, text=jlpt, font=('arial', res.sy(14)), width=res.sx(2),
											bg=self.buttonbg, fg=self.labelsfg, command=lambda jlpt=jlpt: self.select_jlpt(jlpt))
								for jlpt in ('N5', 'N4', 'N3', 'N2', 'N1', '-')}

		self.save(self.chooseJlptFrame, row=1, column=2, padx=res.sx(2), sticky='w')
		self.save(self.jlptTitle, row=0, column=0, padx=res.sx(5), pady=res.sy(2), sticky='w')
		self.save(self.jlptButtonsFrame, row=1, column=0)
		for num, jlpt in enumerate(self.chooseJlptButtons):
			self.save(self.chooseJlptButtons[jlpt], row=0, column=num, padx=res.sx(5), pady=res.sy(5), ipadx=res.sx(3))

		# tags selection button
		self.selectTagsButton = Button(self.addKanjiFrame, text='Select Tag(s)', font=('arial', res.sy(14)), bg=self.buttonbg, fg=self.labelsfg,
									command=self.setup_tags_chooser)
		self.chosenTagsFrame = Frame(self.mainFrame, bg=self.framesbg, width=res.sx(200), height=res.sy(81))
		self.tagsTitle = Label(self.chosenTagsFrame, text='Tag(s):', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.tagsNameLabel = Label(self.chosenTagsFrame, width=res.sx(11), anchor='w', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.displayTagsWindow = Frame(self.chosenTagsFrame, width=res.sx(200), height=res.sy(47), bg='white')
		self.displaySelectedTagsFrame = Frame(self.displayTagsWindow, width=res.sx(198), height=res.sy(45), bg='#000000')

		self.save(self.selectTagsButton, row=3, column=0, pady=res.sy(9))
		self.save(self.chosenTagsFrame, row=1, column=2, columnspan=2, padx=res.sx(3), sticky='e')
		self.save(self.tagsTitle, row=0, column=0, padx=res.sx(5), sticky='w')
		self.save(self.tagsNameLabel, row=0, column=1)
		self.save(self.displayTagsWindow, row=1, column=0, columnspan=2, padx=res.sx(5), pady=res.sy(5), freeze=0)
		self.save(self.displaySelectedTagsFrame, row=0, column=0, padx=res.sx(1), pady=res.sy(1), freeze=0)

		# preview or reset buttons
		self.nextStepFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.previewButton = Button(self.nextStepFrame, text='Preview', font=('arial', res.sy(18)), bg='#b0e8b0', command=self.preview_new_kanji, width=res.sx(7))

		self.save(self.nextStepFrame, row=0, column=3, padx=res.sx(2))
		self.save(self.previewButton, row=0, column=0, padx=res.sx(5), pady=res.sy(17))


	def setup_tags_chooser(self):
		allTags = cfg.getData()[3]
		self.tagsWindow = tags.Tags(allTags, default = self.newTags,
														 update = cfg.update_tags_database,
														 delete = cfg.remove_tag_from_database,
														 exit = self.collapse_tags_chooser)

	def collapse_tags_chooser(self, *args):
		#save selected tags
		self.newTags = [pair[0] for pair in args[0]]

		#clear the tags display frame
		self.clear_tags_display()

		#create new frames from the selected tags.
		for num, pair in enumerate(args[0]):
			tag, bg = pair[0], pair[1]
			tagFrame = Frame(self.displaySelectedTagsFrame, width = res.sx(12), height = res.sy(12), bg = bg)
			tagFrame.bind('<Enter>', lambda *args, tag = tag: self.enter_tag_frame(tag))
			tagFrame.bind('<Leave>', self.leave_tag_frame)

			row = num // 10
			column = num % 10
			padding = res.sy(7 if (num % 2 == 0 and num < 10) else 0)

			tagFrame.grid(row = row, column = column, padx = padding, pady = padding)

	def enter_tag_frame(self, tag):
		self.tagsNameLabel.config(text = tag)

	def leave_tag_frame(self, *args):
		self.tagsNameLabel.config(text = '')

	def clear_tags_display(self):
		for tagFrame in self.displaySelectedTagsFrame.winfo_children():
			tagFrame.destroy()

	def setup_library_info(self, allKanji, **kwargs):
		self.existingKanji = allKanji

		self.invoke_exists = kwargs['invokeExist'] if 'invokeExist' in kwargs else None
		self.cancel_invoke_exists = kwargs['cancelInvokeExist'] if 'cancelInvokeExist' in kwargs else None
		self.previewInvoke = kwargs['previewInvoke'] if 'previewInvoke' in kwargs else self.null
		self.cancelPreviewInvoke = kwargs['cancelpreview'] if 'cancelpreview' in kwargs else self.null

	def get_interface(self):
		self.newKanji = '_new_'
		self.alreadyInKanji = ''

		self.newKanas = ['']
		self.newEngs = ['']

		self.newGrade = ''
		self.newJlpt = ''
		self.newTags = []

		self.wordsPage = 1

	def reset_kanji_details(self):
		self.kanjiEntry.delete(0, END)
		self.clear_words_entries()
		self.reset_grade_jlpt_buttons(self.newGrade, self.newJlpt)
		self.clear_tags_display()
		self.pageLabel.config(text = 1)

	def delete_variables(self):
		del self.newKanji
		del self.alreadyInKanji
		del self.newKanas
		del self.newEngs
		del self.newGrade
		del self.newJlpt
		del self.newTags
		del self.wordsPage

	def reset_grade_jlpt_buttons(self, grade, jlpt):
		if grade != '':
			self.chooseGradeButtons[grade].config(bg = self.buttonbg, fg = self.labelsfg)

		if jlpt != '':
			self.chooseJlptButtons[jlpt].config(bg = self.buttonbg, fg = self.labelsfg)

	def check_kanji_exists(self, *args):
		text = self.kanjiVar.get()

		if text in self.existingKanji:
			self.bringup_invalid(text)
			self.newKanji = ''

		elif text == '':
			self.bringup_null(text)
			self.newKanji = ''

		else:
			self.bringup_valid()
			self.newKanji = text

	def bringup_valid(self):
		self.addKanjiMessage.config(text = 'Valid!', fg = self.labelsfg)
		if self.alreadyInKanji != '' and self.cancel_invoke_exists != None:
			self.cancel_invoke(self.cancel_invoke_exists, self.alreadyInKanji)

	def bringup_invalid(self, kanji):
		self.addKanjiMessage.config(text = 'Already exists!', fg = '#ecc6c6')

		if self.alreadyInKanji != '' and self.invoke_exists != None:
			self.cancel_invoke(self.cancel_invoke_exists, self.alreadyInKanji)
			self.invoke_exists(kanji)
			self.alreadyInKanji = kanji

		elif self.alreadyInKanji == '' and self.invoke_exists != None:
			self.invoke_exists(kanji)

		self.alreadyInKanji = kanji

	def bringup_null(self, kanji):
		self.addKanjiMessage.config(text = '', fg = self.labelsfg)
		if self.alreadyInKanji != '' and self.cancel_invoke_exists != None:
			self.cancel_invoke(self.cancel_invoke_exists, self.alreadyInKanji)

	def cancel_invoke(self, command, kanji):
		command(kanji)
		self.alreadyInKanji = ''

	def change_page(self, step):
		prevPage = self.wordsPage
		if not (self.wordsPage == 1 and step == -1):
			self.wordsPage += step

		#append input information into storage lists
		self.update_words(page = prevPage)
		if len(self.newKanas) < self.wordsPage:
			self.newKanas.append('')
			self.newEngs.append('')

		#clear the entries
		self.clear_words_entries()

		#based on the destination page, insert the correct stored words.
		self.insert_saved_words(page = self.wordsPage - 1, kanas = self.newKanas, engs = self.newEngs)

		self.pageLabel.config(text = self.wordsPage)

	def update_words(self, page):
		self.newKanas[page - 1] = self.kanaEntry.get()
		self.newEngs[page - 1] = self.compile_engs(connector = ',')

	def compile_engs(self, connector):
		connectedText = connector.join([self.englishEntries[num].get() for num in self.englishEntries])
		return connectedText

	def clear_words_entries(self):
		self.kanaEntry.delete(0, END)
		for num in self.englishEntries:
			self.englishEntries[num].delete(0, END)

	def insert_saved_words(self, page, kanas, engs):
		self.kanaEntry.insert(0, kanas[page])
		for num, eng in zip(self.englishEntries, engs[page].split(',')):
			self.englishEntries[num].insert(0, eng)

	def select_grade(self, grade):
		active = ('#33ff77', '#031603')
		if self.newGrade == '':
			self.highlight(self.chooseGradeButtons[grade], bg = active[0], fg = active[1])

		elif self.newGrade != grade:
			self.highlight(self.chooseGradeButtons[self.newGrade], bg = self.buttonbg, fg = self.labelsfg)
			self.highlight(self.chooseGradeButtons[grade], bg = active[0], fg = active[1])

		self.newGrade = grade


	def select_jlpt(self, jlpt):
		active = ('#33ff77', '#031603')
		if self.newJlpt == '':
			self.highlight(self.chooseJlptButtons[jlpt], bg = active[0], fg = active[1])

		elif self.newJlpt != jlpt:
			self.highlight(self.chooseJlptButtons[self.newJlpt], bg = self.buttonbg, fg = self.labelsfg)
			self.highlight(self.chooseJlptButtons[jlpt], bg = active[0], fg = active[1])

		self.newJlpt = jlpt

	def highlight(self, widget, bg, fg):
		widget.config(bg = bg, fg = fg)

	def collapse(self, frame):
		#this function is called when the user has cancelled adding kanji
		self.kanjiEntry.delete(0, END)
		if self.alreadyInKanji != '':
			self.cancel_invoke(self.cancel_invoke_exists, self.alreadyInKanji)
		self.reset_kanji_details()
		self.delete_variables()
		frame.config(width = res.sx(1020)) #<- weird bug with weird fix

	def preview_new_kanji(self):
		#update the current words page
		self.update_words(self.wordsPage)
		reducedWords = self.remove_blanks(self.newKanas, self.newEngs)

		#check if entries are valid
		kanjiValid = (not (self.newKanji in ('_new_', '')) and not (self.newKanji in self.existingKanji))
		wordsValid = reducedWords[0] != []
		gradeValid = (self.newGrade != '')
		jlptValid = (self.newJlpt != '')

		if not (False in (kanjiValid, gradeValid, jlptValid, wordsValid)):
			#all necessary information is added. proceed to preview the kanji.
			newData = {'kanji': self.newKanji, 'words': reducedWords,
						  'grade': self.newGrade, 'jlpt': self.newJlpt, 'tags': self.newTags if self.newTags != [] else ['none']}

			#get the label of the new kanji
			newKanjiLabel = self.previewInvoke(self.newKanji, newData)

	def remove_blanks(self, kanas, engs):
		kanaList, engList = [], []
		for kana, eng in zip(kanas, engs):
			if not ((kana == '') or eng.split(',').count('') == 5):
				kanaList.append(kana)
				engList.append(eng)

		return (kanaList, engList)



class deleting_editor(editor):
	mainBg = '#240f0f'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

		self.mainFrame.config(bg = self.mainBg)

		self.titleLabel = Label(self.mainFrame, text='Kanji selected to delete', font=('arial', res.sy(18)), bg=self.mainBg, fg='#eddede')
		self.save(self.titleLabel, row=0, column=0, pady=res.sy(7))

		self.pendingKanjiWindow = Frame(self.mainFrame, bg='#e08585')
		self.pendingKanjiFrame = Frame(self.pendingKanjiWindow, width=res.sx(879), height=res.sy(135), bg='#330000')

		self.save(self.pendingKanjiWindow, row=1, column=0, padx=res.sx(5))
		self.save(self.pendingKanjiFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2), freeze=0)

		self.buttonsFrame = Frame(self.mainFrame, bg=self.mainBg)
		self.deleteButton = Button(self.buttonsFrame, text='Delete', font=('arial', res.sy(18)), bg='#330000', fg='#e4cdcd', width=res.sx(7),
								command=self.delete_kanji)
		self.clearButton = Button(self.buttonsFrame, text='Clear', font=('arial', res.sy(18)), bg='#330000', fg='#e4e4cd', width=res.sx(7),
								command=self.clear_pending_kanji)

		self.save(self.buttonsFrame, row=1, column=1, padx=res.sx(9))
		self.save(self.deleteButton, row=0, column=0, pady=res.sy(10))
		self.save(self.clearButton, row=1, column=0, pady=res.sy(10))


	def setup_library_info(self, allKanji, **kwargs):
		self.invokeClear = kwargs['clearinvoke'] if 'clearinvoke' in kwargs else self.null
		self.invokeDelete = kwargs['deleteinvoke'] if 'deleteinvoke' in kwargs else self.null

	def get_interface(self):
		self.pendingDict = {}

	def collapse(self, frame):
		for kanji in self.pendingDict:
			self.pendingDict[kanji].destroy()

		self.delete_variables()
		frame.config(width = res.sx(1020))

	def delete_variables(self):
		del self.pendingDict

	def select_deleting_kanji(self, kanji):
		if kanji in self.pendingDict:
			fullList = [kanji for kanji in self.pendingDict]
			removedPos = fullList.index(kanji)
			shiftList = fullList[removedPos + 1:]
			self.shift_labels(shiftList, removedPos, -1)
			self.pendingDict[kanji].destroy()
			del self.pendingDict[kanji]

		else:
			self.pendingDict[kanji] = self.create_deleting_label(kanji)

		return (kanji in self.pendingDict)

	def create_deleting_label(self, kanji):
		fg = {1: '#ffd5cc', 2: '#ddffcc', 3: '#ccf6ff', 4: '#ffccf6'}[len(kanji)]
		row, column = self.get_coordinates(len(self.pendingDict))
		label = Label(self.pendingKanjiFrame, text = kanji[0], font = ('times', res.sy(20)), bg = '#330000', fg = fg)
		label.grid(row = row, column = column, padx = res.sx(5), pady = res.sx(5) if (column % 2 == 0) else 0)

		return label

	def shift_labels(self, shiftLabels, startPos, shiftAmount):
		for pos, kanji in enumerate(shiftLabels, start = 1):
			row, column = self.get_coordinates(startPos + pos + shiftAmount)
			self.pendingDict[kanji].grid_configure(row = row, column = column)

	def get_coordinates(self, position):
		row = position // 20
		column = position % 20
		return (row, column)

	def clear_pending_kanji(self):
		for kanji in self.pendingDict:
			self.invokeClear(kanji)
			self.pendingDict[kanji].destroy()
		self.pendingDict.clear()

	def delete_kanji(self):
		deleteKanjiList = [kanji for kanji in self.pendingDict]
		self.clear_pending_kanji()
		self.invokeDelete(deleteKanjiList)


class editing_editor(editor):
	mainBg = '#dbddf0'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

		self.framesbg = '#132039'
		self.labelsfg = '#e5e5ff'
		self.buttonsbg = '#141452'


		self.mainFrame.config(bg = self.mainBg)

		self.editWordsFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.wordsTitle = Label(self.editWordsFrame, text='Kana & english', font=('arial', res.sy(16)), bg=self.framesbg, fg=self.labelsfg)
		self.kanaEntry = Entry(self.editWordsFrame, font=('arial', res.sy(18)), width=res.sx(12), justify=CENTER)
		self.kanaCharButton = Button(self.editWordsFrame, text='あ', font=('times', res.sy(14), 'bold'))
		self.editingTranslator = translator.Translator(self.kanaEntry, ['あ', 'ア'], self.kanaCharButton)
		self.englishEntryFrame = Frame(self.editWordsFrame, bg=self.framesbg)
		self.englishEntries = {num: Entry(self.englishEntryFrame, font=('arial', res.sy(18)), width=res.sx(10), justify=CENTER) for num in range(5)}
		self.pageFrame = Frame(self.editWordsFrame, bg=self.framesbg)
		self.pageLabel = Label(self.pageFrame, text='1', font=('times', res.sy(16)), bg=self.framesbg, fg=self.labelsfg)
		self.pageUpButton = Button(self.pageFrame, text=u'\u25b2', font=('arial', res.sy(8)), width=res.sx(3), command=lambda: self.change_page(-1))
		self.pageDownButton = Button(self.pageFrame, text=u'\u25bc', font=('arial', res.sy(8)), width=res.sx(3), command=lambda: self.change_page(1))

		self.save(self.editWordsFrame, row=0, column=0, pady=res.sy(2), ipady=res.sy(1), padx=res.sx(15), rowspan=2)
		self.save(self.wordsTitle, row=0, column=0, pady=res.sy(5), columnspan=2)
		self.save(self.kanaEntry, row=1, column=0, padx=res.sx(5), columnspan=2)
		self.save(self.kanaCharButton, row=2, column=1, pady=res.sy(5))
		self.save(self.englishEntryFrame, row=0, column=2, pady=res.sy(5), rowspan=3)
		for num in self.englishEntries:
			self.save(self.englishEntries[num], row=num, column=0, padx=res.sx(5), pady=res.sy(2))
		self.save(self.pageFrame, row=2, column=0)
		self.save(self.pageLabel, row=0, column=0, padx=res.sx(10), pady=res.sy(10), rowspan=2)
		self.save(self.pageUpButton, row=0, column=1)
		self.save(self.pageDownButton, row=1, column=1)


		# section for choosing grade
		self.chooseGradeFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.gradeTitle = Label(self.chooseGradeFrame, text='Edit grade', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.gradeButtonsFrame = Frame(self.chooseGradeFrame, bg=self.framesbg)
		self.chooseGradeButtons = {
			grade: Button(
				self.gradeButtonsFrame,
				text=grade,
				font=('arial', res.sy(14)),
				width=res.sx(2),
				bg=self.buttonsbg,
				fg=self.labelsfg,
				command=lambda grade=grade: self.select_grade(grade)
			)
			for grade in ('1', '2', '3', '4', '5', '6', 'JH', '-')
		}

		self.save(self.chooseGradeFrame, row=0, column=1, padx=res.sx(2))
		self.save(self.gradeTitle, row=0, column=0, padx=res.sx(5), pady=res.sy(2), sticky='w')
		self.save(self.gradeButtonsFrame, row=1, column=0)
		for num, grade in enumerate(self.chooseGradeButtons):
			self.save(self.chooseGradeButtons[grade], row=0, column=num, padx=res.sx(5), pady=res.sy(5), ipadx=res.sx(3))

		# section for choosing JLPT
		self.chooseJlptFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.jlptTitle = Label(self.chooseJlptFrame, text='Edit JLPT', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.jlptButtonsFrame = Frame(self.chooseJlptFrame, bg=self.framesbg)
		self.chooseJlptButtons = {
			jlpt: Button(
				self.jlptButtonsFrame,
				text=jlpt,
				font=('arial', res.sy(14)),
				width=res.sx(2),
				bg=self.buttonsbg,
				fg=self.labelsfg,
				command=lambda jlpt=jlpt: self.select_jlpt(jlpt)
			)
			for jlpt in ('N5', 'N4', 'N3', 'N2', 'N1', '-')
		}

		self.save(self.chooseJlptFrame, row=1, column=1, padx=res.sx(2), sticky='w')
		self.save(self.jlptTitle, row=0, column=0, padx=res.sx(5), pady=res.sy(2), sticky='w')
		self.save(self.jlptButtonsFrame, row=1, column=0)
		for num, jlpt in enumerate(self.chooseJlptButtons):
			self.save(self.chooseJlptButtons[jlpt], row=0, column=num, padx=res.sx(5), pady=res.sy(5), ipadx=res.sx(3))




		# phase buttons
		self.phaseButtonsFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.previewEditButton = Button(self.phaseButtonsFrame, text='Preview', font=('arial', res.sy(18)), bg='#000033', fg='#cdcde4', width=res.sx(7), command=self.preview_edited_kanji)
		self.deselectButton = Button(self.phaseButtonsFrame, text='Deselect', font=('arial', res.sy(18)), bg='#000033', fg='#cdcde4', width=res.sx(7), command=self.deselect_kanji)

		self.save(self.phaseButtonsFrame, row=0, column=2, padx=res.sx(10))
		self.save(self.previewEditButton, row=0, column=0, padx=res.sx(10), pady=res.sy(17))
		self.save(self.deselectButton, row=0, column=1, padx=res.sx(10))

		# editing tags section
		self.tagsFrame = Frame(self.mainFrame, bg=self.framesbg)
		self.tagsTitle = Label(self.tagsFrame, text='Tag(s):', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.tagsNameLabel = Label(self.tagsFrame, width=res.sx(11), anchor='w', font=('arial', res.sy(14)), bg=self.framesbg, fg=self.labelsfg)
		self.displayTagsWindow = Frame(self.tagsFrame, width=res.sx(200), height=res.sy(47), bg='white')
		self.displaySelectedTagsFrame = Frame(self.displayTagsWindow, width=res.sx(198), height=res.sy(45), bg='#000000')
		self.editTagsButton = Button(self.tagsFrame, text='Edit tags', font=('arial', res.sy(16)), bg='#000033', fg='#cdcde4', command=self.edit_tags)

		self.save(self.tagsFrame, row=1, column=1, columnspan=2, sticky='e', padx=res.sx(10))
		self.save(self.tagsTitle, row=0, column=0, padx=res.sx(5), sticky='w')
		self.save(self.tagsNameLabel, row=0, column=1)
		self.save(self.displayTagsWindow, row=1, column=0, columnspan=2, padx=res.sx(5), pady=res.sy(5), freeze=0)
		self.save(self.displaySelectedTagsFrame, row=0, column=0, padx=res.sx(1), pady=res.sy(1), freeze=0)
		self.save(self.editTagsButton, row=1, column=2, padx=res.sx(20))



	def get_interface(self, **kwargs):
		self.get_edit_variables()

	def get_edit_variables(self):
		self.editingKanji = ''
		self.wordsPage = 1
		self.pageLabel.config(text = 1)

	def setup_library_info(self, allKanji, **kwargs):
		self.invokeSelect = kwargs['selectinvoke'] if 'selectinvoke' in kwargs else self.null()
		self.invokeDeselect = kwargs['deselectinvoke'] if 'deselectinvoke' in kwargs else self.null()
		self.invokePreview = kwargs['previewinvoke'] if 'previewinvoke' in kwargs else self.null()


	def setup_editing_variables(self, info):
		self.editingKanas = [kana for kana in info[0]]
		self.uneditedKanas = tuple([kana for kana in info[0]])

		self.editingEngs = [info[0][kana] for kana in info[0]]
		self.uneditedEngs = [tuple(info[0][kana]) for kana in info[0]]

		self.editingGrade = info[1]
		self.uneditedGrade = info[1]

		self.editingJlpt = info[2]
		self.uneditedJlpt = info[2]

		self.editingTags = info[3]
		self.uneditedTags = tuple(info[3])

	def select_editing_kanji(self, kanji, fulldetails, tagcolours):
		self.editingKanji = kanji
		self.setup_editing_variables(fulldetails)
		self.setup_words(self.editingKanas, self.editingEngs)
		self.setup_default_grade_button(self.uneditedGrade)
		self.setup_default_jlpt_button(self.uneditedJlpt)
		self.setup_default_tags(self.uneditedTags, tagcolours)

		self.invokeSelect(kanji)
		self.pageLabel.config(text = self.wordsPage)

	def setup_words(self, kanas, engs):
		self.kanaEntry.insert(0, kanas[0])
		for num, eng in enumerate(engs[0]):
			self.englishEntries[num].insert(0, eng)

	def change_page(self, step):
		prevPage = self.wordsPage
		if not (self.wordsPage == 1 and step == -1):
			self.wordsPage += step

		#append input information into storage lists
		self.update_words(prevPage)

		if len(self.editingKanas) < self.wordsPage:
			self.editingKanas.append('')
			self.editingEngs.append([''])

		#clear entries
		self.clear_words_entries()

		#based on destination page, insert the correct stored words.
		self.insert_saved_words(page = self.wordsPage - 1, kanas = self.editingKanas, engs = self.editingEngs)

		self.pageLabel.config(text = self.wordsPage)

	def insert_saved_words(self, page, kanas, engs):
		self.kanaEntry.insert(0, kanas[page])
		for num, eng in zip(self.englishEntries, engs[page]):
			self.englishEntries[num].insert(0, eng)

	def update_words(self, page):
		editedKana = self.kanaEntry.get()
		editedEngs = [self.englishEntries[num].get() for num in self.englishEntries]
		self.editingKanas[page - 1] = editedKana
		self.editingEngs[page - 1] = editedEngs

	def clear_words_entries(self):
		self.kanaEntry.delete(0, END)
		for num in self.englishEntries:
			self.englishEntries[num].delete(0, END)

	def select_grade(self, grade):
		active = ('#33bbff', '#030316')
		if self.editingKanji != '':
			self.chooseGradeButtons[self.editingGrade].config(bg = self.buttonsbg, fg = self.labelsfg)
			self.editingGrade = grade
			self.chooseGradeButtons[grade].config(bg = active[0], fg = active[1])

	def select_jlpt(self, jlpt):
		active = ('#33bbff', '#030316')
		if self.editingKanji != '':
			self.chooseJlptButtons[self.editingJlpt].config(bg = self.buttonsbg, fg = self.labelsfg)
			self.editingJlpt = jlpt
			self.chooseJlptButtons[jlpt].config(bg = active[0], fg = active[1])

	def setup_default_grade_button(self, grade):
		active = ('#33bbff', '#030316')
		self.chooseGradeButtons[grade].config(bg = active[0], fg = active[1])

	def setup_default_jlpt_button(self, jlpt):
		active = ('#33bbff', '#030316')
		self.chooseJlptButtons[jlpt].config(bg = active[0], fg = active[1])

	def setup_default_tags(self, tags, colours):
		for num, tag in enumerate(tags):
			hexCol = colours[tag]
			tagIcon = self.create_tag_icon(tag, hexCol, num)

	def create_tag_icon(self, tag, bg, pos):
		tagFrame = Frame(self.displaySelectedTagsFrame, width = res.sx(12), height = res.sy(12), bg = bg)

		tagFrame.bind('<Enter>', lambda *args, tag = tag: self.hover_tag_frame(tag))
		tagFrame.bind('<Leave>', lambda *args: self.hover_tag_frame(''))

		padding = res.sy(7 if (pos % 2 == 0 and pos < 10) else 0)
		tagFrame.grid(row = pos // 10, column = pos % 10, padx = padding, pady = padding)

	def edit_tags(self):
		if self.editingKanji != '':
			allTags = cfg.getData()[3]
			self.tagsWindow = tags.Tags(allTags, default = self.editingTags,
															 update = cfg.update_tags_database,
															 delete = cfg.remove_tag_from_database,
															 exit = self.collapse_tags_chooser)

	def collapse_tags_chooser(self, tagslist):
		self.editingTags = [pair[0] for pair in tagslist]
		self.clear_tag_frame()
		for num, pair in enumerate(tagslist):
			self.create_tag_icon(pair[0], pair[1], num)

	def hover_tag_frame(self, tag):
		self.tagsNameLabel.config(text = tag)

	def collapse(self, frame):
		if self.editingKanji != '':
			self.refresh_edit_editor()
		self.delete_variables()
		frame.config(width = res.sx(1020))

	def delete_variables(self):
		del self.editingKanji
		del self.wordsPage

	def deselect_kanji(self):
		if self.editingKanji != '':
			self.invokeDeselect(self.editingKanji)
			self.clear_words_entries()
			self.reset_grade_jlpt_buttons(self.editingGrade, self.editingJlpt)
			self.clear_tag_frame()
			self.pageLabel.config(text = 1)
			self.editingKanji = ''
		else:
			print('none selected')

	def reset_grade_jlpt_buttons(self, grade, jlpt):
		if grade != '':
			self.chooseGradeButtons[grade].config(bg = self.buttonsbg, fg = self.labelsfg)

		if jlpt != '':
			self.chooseJlptButtons[jlpt].config(bg = self.buttonsbg, fg = self.labelsfg)

	def clear_tag_frame(self):
		for frame in self.displaySelectedTagsFrame.winfo_children():
			frame.destroy()

	def preview_edited_kanji(self):
		if self.editingKanji != '':
			self.update_words(self.wordsPage)
			details = {'words': self.compress_words(self.editingKanas, self.editingEngs),
						  'grade': self.editingGrade,
						  'jlpt': self.editingJlpt,
						  'tags': self.editingTags}
			self.invokePreview(self.editingKanji, details)

		else:
			print('cant preview without selected kanji')

	def compress_words(self, kanas, engs):
		wordsDict = {}
		for kana, eng in zip(kanas, engs):
			if not ((kana == '') or (eng.count('') == 5)):
				wordsDict[kana] = [text for text in eng if text != '']
		return wordsDict

	def refresh_edit_editor(self):
		self.clear_words_entries()
		self.reset_grade_jlpt_buttons(self.editingGrade, self.editingJlpt)
		self.clear_tag_frame()

class adding_hiragana_editor(editor):
	mainBg = '#131f13'
	lightBg = '#e2e9e2'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

		self.mainFrame.config(bg = self.mainBg)

		self.hiraganaWin = Frame(self.mainFrame, bg = self.lightBg)
		self.meaningsWin = Frame(self.mainFrame, bg = self.lightBg)
		self.kanjiWin = Frame(self.mainFrame, bg = self.lightBg)
		self.addWin = Frame(self.mainFrame, bg = '#dfecdf')

		self.save(self.hiraganaWin, row=0, column=0, padx=res.sx(5), pady=res.sy(5), rowspan=2)
		self.save(self.meaningsWin, row=0, column=1, rowspan=2)
		self.save(self.kanjiWin, row=0, column=2, padx=res.sx(5), pady=res.sy(5), sticky='n')
		self.save(self.addWin, row=1, column=2, sticky='n')

		self.hiraganaFrame = Frame(self.hiraganaWin, bg=self.mainBg)
		self.meaningsFrame = Frame(self.meaningsWin, bg=self.mainBg)
		self.kanjiFrame = Frame(self.kanjiWin, bg=self.mainBg)
		self.addFrame = Frame(self.addWin, bg=self.mainBg)

		self.save(self.hiraganaFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2))
		self.save(self.meaningsFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2))
		self.save(self.kanjiFrame, row=0, column=9, padx=res.sx(2), pady=res.sy(2))
		self.save(self.addFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2))

		self.newKanaTitle = Label(self.hiraganaFrame, text='New word/phrase', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)
		self.newKanaEntry = Entry(self.hiraganaFrame, font=('arial', res.sy(20)), width=res.sx(12))
		self.hiraganaTranslator = translator.Translator(self.newKanaEntry, ['あ'])
		self.newKanaMsg = Label(self.hiraganaFrame, text='Valid!', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)

		self.save(self.newKanaTitle, row=0, column=0, pady=res.sy(20))
		self.save(self.newKanaEntry, row=1, column=0, padx=res.sx(20))
		self.save(self.newKanaMsg, row=2, column=0, pady=res.sy(20))

		self.newMeaningsTitle = Label(self.meaningsFrame, text='English translation(s)', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)
		self.newMeaningVars = [StringVar(name=f'new meaning {num}') for num in range(6)]
		self.newMeaningEntries = [Entry(self.meaningsFrame, font=('arial', res.sy(20)), width=res.sx(10), textvariable=self.newMeaningVars[num]) for num in range(6)]
		self.spacing = Label(self.meaningsFrame, bg=self.mainBg, font=('arial', res.sy(20)))

		self.save(self.newMeaningsTitle, row=0, column=0, pady=res.sy(10), columnspan=3)
		for num, entry in enumerate(self.newMeaningEntries):
			padding = res.sx(8) if num in (0, 2) else 0
			self.save(entry, row=(num // 3) + 1, column=num % 3, padx=padding, pady=padding)
		self.save(self.spacing, row=3, column=0)

		self.newKanjiTitle = Label(self.kanjiFrame, text='Kanji (optional)', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)
		self.newKanjiVar = StringVar(name='new kanji')
		self.newKanjiEntry = Entry(self.kanjiFrame, font=('times', res.sy(18)), width=res.sx(10), textvariable=self.newKanjiVar)

		self.save(self.newKanjiTitle, row=0, column=0, pady=res.sy(8))
		self.save(self.newKanjiEntry, row=1, column=0, pady=res.sy(8), padx=res.sx(60))

		self.addButton = Button(self.addFrame, text='Add', font=('arial', res.sy(18)), bg='#d9f2d9', width=res.sx(6))
		self.save(self.addButton, row=0, column=0, padx=res.sx(75), pady=res.sy(11))


	def setup(self, **kwargs):
		invokeAdd = kwargs['addinvoke'] if 'addinvoke' in kwargs else self.null
		self.addButton.config(command = invokeAdd)

	def get_interface(self):
		self.newKanaEntry.focus_set()

	def collapse(self):
		self.clear_all_entries()

	def get_new_hiragana(self):
		newKana = self.newKanaEntry.get()
		newMeanings = ','.join([var.get() for var in self.newMeaningVars if var.get() != ''])
		newKanji = self.newKanjiVar.get() if self.newKanjiVar.get() != '' else '-'

		return (newKana, newMeanings, newKanji)

	def clear_all_entries(self):
		self.newKanaEntry.delete(0, END)
		self.newKanjiEntry.delete(0, END)
		for entry in self.newMeaningEntries:
			entry.delete(0, END)

	def get_vars(self):
		return (self.hiraganaTranslator.textVar, self.newKanjiVar, *self.newMeaningVars)


class deleting_hiragana_editor(editor):
	mainBg = '#240f0f'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

	def get_interface(self):
		pass

	def collapse(self):
		pass


class editing_hiragana_editor(editor):
	mainBg = '#dbddf0'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

	def get_interface(self):
		pass

	def collapse(self):
		pass




class adding_katakana_editor(editor):
	mainBg = '#131f13'
	lightBg = '#e2e9e2'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

		self.mainFrame.config(bg = self.mainBg)

		self.katakanaWin = Frame(self.mainFrame, bg = self.lightBg)
		self.meaningsWin = Frame(self.mainFrame, bg = self.lightBg)
		self.addWin = Frame(self.mainFrame, bg = '#dfecdf')

		self.save(self.katakanaWin, row=0, column=0, padx=res.sx(5), pady=res.sy(5))
		self.save(self.meaningsWin, row=0, column=1)
		self.save(self.addWin, row=0, column=2, padx=res.sx(5), pady=res.sy(5), sticky='n')

		self.katakanaFrame = Frame(self.katakanaWin, bg=self.mainBg)
		self.meaningsFrame = Frame(self.meaningsWin, bg=self.mainBg)
		self.addFrame = Frame(self.addWin, bg=self.mainBg)

		self.save(self.katakanaFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2))
		self.save(self.meaningsFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2))
		self.save(self.addFrame, row=0, column=0, padx=res.sx(2), pady=res.sy(2))

		self.newKanaTitle = Label(self.katakanaFrame, text='New word/phrase', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)
		self.newKanaEntry = Entry(self.katakanaFrame, font=('arial', res.sy(20)), width=res.sx(12))
		self.katakanaTranslator = translator.Translator(self.newKanaEntry, ['ア'])
		self.newKanaMsg = Label(self.katakanaFrame, text='Valid!', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)

		self.save(self.newKanaTitle, row=0, column=0, pady=res.sy(20))
		self.save(self.newKanaEntry, row=1, column=0, padx=res.sx(20))
		self.save(self.newKanaMsg, row=2, column=0, pady=res.sy(20))

		self.newMeaningsTitle = Label(self.meaningsFrame, text='English translation(s)', font=('arial', res.sy(16)), bg=self.mainBg, fg=self.lightBg)
		self.newMeaningVars = [StringVar(name=f'new meaning {num}') for num in range(6)]
		self.newMeaningEntries = [Entry(self.meaningsFrame, font=('arial', res.sy(20)), width=res.sx(10), textvariable=self.newMeaningVars[num]) for num in range(6)]
		self.spacing = Label(self.meaningsFrame, bg=self.mainBg, font=('arial', res.sy(20)))

		self.save(self.newMeaningsTitle, row=0, column=0, pady=res.sy(10), columnspan=3)
		for num, entry in enumerate(self.newMeaningEntries):
			padding = res.sx(8) if num in (0, 2) else 0
			self.save(entry, row=(num // 3) + 1, column=num % 3, padx=padding, pady=padding)
		self.save(self.spacing, row=3, column=0)

		self.addButton = Button(self.addFrame, text='Add', font=('arial', res.sy(18)), bg='#d9f2d9', width=res.sx(6))
		self.save(self.addButton, row=0, column=0, padx=res.sx(75), pady=res.sy(64))


	def get_interface(self):
		self.newKanaEntry.focus_set()

	def setup(self, **kwargs):
		invokeAdd = kwargs['addinvoke'] if 'addinvoke' in kwargs else self.null()
		self.addButton.config(command = invokeAdd)

	def collapse(self):
		self.clear_all_entries()

	def get_new_katakana(self):
		newKana = self.newKanaEntry.get()
		newMeanings = ','.join([var.get() for var in self.newMeaningVars if var.get() != ''])

		return (newKana, newMeanings)

	def clear_all_entries(self):
		self.newKanaEntry.delete(0, END)
		for entry in self.newMeaningEntries:
			entry.delete(0, END)

	def get_vars(self):
		return (self.katakanaTranslator.textVar, *self.newMeaningVars)


class deleting_katakana_editor(editor):
	mainBg = '#240f0f'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

	def get_interface(self):
		pass

	def collapse(self):
		pass
		

class editing_katakana_editor(editor):
	mainBg = '#dbddf0'

	def __init__(self, In, width, height):
		super().__init__(In, width, height)

	def get_interface(self):
		pass

	def collapse(self):
		pass