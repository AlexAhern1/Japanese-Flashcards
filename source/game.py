#module for handling flashcard games
from tkinter import *
from random import choice

from client import Window
import translator
import resolution as res

class Game_Interface(Window):
	FPS = 25 # (frames per second of the game interface)

	def __init__(self, root, **kwargs):

		super().__init__(root, **kwargs)

		self.save_colours(('history win', '#ffccff'), ('action win', '#cce5ff'), ('perf win', '#ccffcc'),
						  ('history frm', '#161216'), ('action frm', '#121416'), ('perf frm', '#121612'),
						  ('message fg', '#e2ccff'), ('message win', '#ffffff'), ('message bg', '#000000'),
						  ('writing start bg', '#433960'), ('writing bg', '#244242'), ('writing fg', '#e9e9fb'), 
						  ('buttons bg', '#2e2e38'), ('buttons fg', '#e0e0eb'),
						  ('correct button bg', '#004d00'), ('wrong button bg', '#4d0000'), 
						  ('lives fg', '#99ff66'), ('timer fg', '#40bf40'), ('stats fg', '#33ff88'),
						  ('retry bg', '#1b321b'), ('return bg', '#321b1b'), ('end fg', '#e7e7e4'))

		# frame containing all records of answered kanji with some details like correct / wrong answer inputs
		self.historyWindow = self.new_Frame(
			self.mainWin, width=res.sx(400), height=res.sy(680), bg=self.col['history win'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(5), pady=res.sy(5))
		)
		self.historyFrame = self.new_Frame(
			self.historyWindow, width=res.sx(396), height=res.sy(430), bg=self.col['history frm'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(2), pady=res.sy(1), freeze=1, sticky='s')
		)

		self.practiceMistakesFrame = self.new_Frame(
			self.historyWindow, width=res.sx(396), height=res.sy(60), bg=self.col['history frm'],
			geom=self.set_geom(row=1, column=0, freeze=1)
		)

		self.practiceMistakesButton = self.new_Button(
			self.practiceMistakesFrame, text='Practice Mistakes', font=('arial', res.sy(16)),
			bg='#34192f', fg='#ddd5d5',
			command=lambda: self.practice_mistakes(self.mistakes),
			geom=self.set_geom(row=0, column=0, padx=res.sx(105), pady=res.sy(10), hidden=1)
		)

		self.historyDetailsFrame = self.new_Frame(
			self.historyWindow, width=res.sx(396), height=res.sy(184), bg='#000000',
			geom=self.set_geom(row=2, column=0, pady=res.sy(1), freeze=1, sticky='n')
		)

		self.historyKanjiLabel = self.new_Label(
			self.historyDetailsFrame, font=('times', res.sy(40)), bg='#000000', fg='#ff4444',
			geom=self.set_geom(row=0, column=0, pady=res.sy(3), sticky='w')
		)

		self.historyKanaLabel = self.new_Label(
			self.historyDetailsFrame, font=('arial', res.sy(18)), bg='#000000', fg='#ff4444',
			geom=self.set_geom(row=1, column=0, sticky='w')
		)

		self.historyEnglishLabel = self.new_Label(
			self.historyDetailsFrame, font=('arial', res.sy(14)), bg='#000000', fg='#ff4444',
			geom=self.set_geom(row=2, column=0, pady=res.sy(3), sticky='w')
		)

		self.historyInputLabel = self.new_Label(
			self.historyDetailsFrame, font=('arial', res.sy(18)), bg='#000000', fg='#ff4444',
			geom=self.set_geom(row=3, column=0, sticky='w')
		)


		# frame containing the interactive aspect of the window, like submitting answers, moving to the next flashcard, etc.
		self.actionWindow = self.new_Frame(
			self.mainWin, width=res.sx(400), height=res.sy(680), bg=self.col['action win'],
			geom=self.set_geom(row=0, column=1)
		)

		self.flashcardFrame = self.new_Frame(
			self.actionWindow, width=res.sx(396), height=res.sy(396), bg=self.col['action frm'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(2), pady=res.sy(2), freeze=1)
		)

		self.flashcardLabel = self.new_Label(
			self.flashcardFrame, font=('times', res.sy(58)), anchor='center',
			bg=self.col['action frm'], width=9,
			geom=self.set_geom(row=0, column=0, ipadx=res.sx(1), pady=res.sy(152), hidden=1)
		)

		self.kanaFrame = self.new_Frame(
			self.flashcardFrame, width=res.sx(396), height=res.sy(120), bg=self.col['action frm'],
			geom=self.set_geom(row=0, column=0, freeze=1, hidden=1)
		)
		self.kanaLabel = self.new_Label(
			self.kanaFrame, fg='#ffffff', bg=self.col['action frm'], font=('arial', res.sy(18)), width=28,
			geom=self.set_geom(row=0, column=1, pady=res.sy(10), hidden=1)
		)

		self.showKanaButton = self.new_Button(
			self.kanaFrame, text='Show', font=('arial', res.sy(16)), bg=self.col['action win'], fg='#000000',
			state=DISABLED,
			geom=self.set_geom(row=0, column=0, padx=res.sx(5), hidden=1)
		)

		self.englishFrame = self.new_Frame(
			self.flashcardFrame, width=res.sx(396), height=res.sy(276), bg=self.col['action frm'],
			geom=self.set_geom(row=1, column=0, freeze=1, hidden=1)
		)
		self.englishLabel = self.new_Label(
			self.englishFrame, fg='#ffffff', bg=self.col['action frm'], font=('arial', res.sy(18)), width=28, justify='w',
			geom=self.set_geom(row=0, column=0, pady=res.sy(10), hidden=1)
		)

		self.answerFrame = self.new_Frame(
			self.actionWindow, width=res.sx(396), height=res.sy(200), bg=self.col['action frm'],
			geom=self.set_geom(row=1, column=0, freeze=1)
		)

		self.answerMessageWin = self.new_Frame(
			self.answerFrame, bg=self.col['message win'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(10), pady=res.sy(10))
		)

		self.answerMessageLabel = self.new_Label(
			self.answerMessageWin, font=('arial', res.sy(30)), borderwidth=2, relief='solid', width=16,
			bg=self.col['message bg'], fg=self.col['message fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(1), pady=res.sy(1))
		)

		self.submitVocabEntry = self.new_Entry(
			self.answerFrame, font=('arial', res.sy(32)), width=12, justify='center',
			geom=self.set_geom(row=1, column=0, pady=res.sy(30), hidden=1)
		)
		self.translator = translator.Translator(self.submitVocabEntry, ['あ', 'ABC'])


		self.startWritingButton = self.new_Button(
			self.answerFrame, font=('arial', res.sy(20)), text='Begin', width=7,
			bg=self.col['writing start bg'], fg=self.col['writing fg'],
			command=self.start_writing_game,
			geom=self.set_geom(row=1, column=0, hidden=1, pady=res.sy(30))
		)

		self.checkWritingButton = self.new_Button(
			self.answerFrame, font=('arial', res.sy(20)), text='Check', width=7,
			bg=self.col['writing bg'], fg=self.col['writing fg'],
			command=lambda: self.check_writing_answer(),
			geom=self.set_geom(row=1, column=0, hidden=1, pady=res.sy(30))
		)

		self.checkWritingFrame = self.new_Frame(
			self.answerFrame, bg=self.col['action frm'],
			geom=self.set_geom(row=1, column=0, pady=res.sy(30), hidden=1)
		)

		self.correctWritingButton = self.new_Button(
			self.checkWritingFrame, font=('arial', res.sy(20)), text='✓', width=3,
			bg=self.col['correct button bg'], fg='#ffffff',
			command=lambda: self.tabulate_writing(correct=True),
			geom=self.set_geom(row=1, column=0, padx=res.sx(10), hidden=1)
		)

		self.wrongWritingButton = self.new_Button(
			self.checkWritingFrame, font=('arial', res.sy(20)), text='❌', width=3,
			bg=self.col['wrong button bg'], fg='#ffffff',
			command=lambda: self.tabulate_writing(correct=False),
			geom=self.set_geom(row=1, column=1, padx=res.sx(10), hidden=1)
		)

		self.endButtonsFrame = self.new_Frame(
			self.answerFrame, bg=self.col['action frm'],
			geom=self.set_geom(row=1, column=0, pady=res.sy(34), hidden=1)
		)

		self.retryButton = self.new_Button(
			self.endButtonsFrame, font=('arial', res.sy(18)), text='Retry', width=7,
			bg=self.col['retry bg'], fg=self.col['end fg'],
			command=self.retry_game,
			geom=self.set_geom(row=0, column=0, padx=res.sx(25), hidden=1)
		)

		self.returnButton = self.new_Button(
			self.endButtonsFrame, font=('arial', res.sy(18)), text='Return', width=7,
			bg=self.col['return bg'], fg=self.col['end fg'],
			command=self.exit_game,
			geom=self.set_geom(row=0, column=1, padx=res.sx(25), hidden=1)
		)



		self.buttonsFrame = self.new_Frame(
			self.actionWindow, width=res.sx(396), height=res.sy(76), bg=self.col['action frm'],
			geom=self.set_geom(row=2, column=0, pady=res.sy(2), freeze=1)
		)

		self.hintButton = self.new_Button(
			self.buttonsFrame, text='Hint', font=('arial', res.sy(16)), width=5,
			bg=self.col['buttons bg'], fg=self.col['buttons fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(47), pady=res.sy(18))
		)

		self.skipButton = self.new_Button(
			self.buttonsFrame, text='Skip', font=('arial', res.sy(16)), width=5,
			bg=self.col['buttons bg'], fg=self.col['buttons fg'],
			geom=self.set_geom(row=0, column=1)
		)

		self.quitButton = self.new_Button(
			self.buttonsFrame, text='Quit', font=('arial', res.sy(16)), width=5,
			bg=self.col['buttons bg'], fg=self.col['buttons fg'],
			command=self.end_game,
			geom=self.set_geom(row=0, column=2, padx=res.sx(47))
		)


		# frame for monitoring and updating performance
		self.perfWindow = self.new_Frame(
			self.mainWin, width=res.sx(400), height=res.sy(680), bg=self.col['perf win'],
			geom=self.set_geom(row=0, column=2, padx=res.sx(5))
		)

		self.metersFrame = self.new_Frame(
			self.perfWindow, width=res.sx(250), height=res.sy(300), bg=self.col['perf frm'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(1), pady=res.sy(2), freeze=1, sticky='e')
		)

		self.checkKanjiLabel = self.new_Label(
			self.metersFrame, font=('times', res.sy(40)), bg=self.col['perf frm'], fg='#ffffff', width=8,
			geom=self.set_geom(row=0, column=0, pady=res.sy(113), ipadx=res.sx(2), hidden=1)
		)

		self.clockFrame = self.new_Frame(
			self.perfWindow, width=res.sx(144), height=res.sy(300), bg=self.col['perf frm'],
			geom=self.set_geom(row=0, column=1, padx=res.sx(1), freeze=1, sticky='w')
		)

		self.clockCanvas = self.new_Canvas(
			self.clockFrame, width=res.sx(140), height=res.sy(140), bg=self.col['perf frm'],
			bd=0, highlightthickness=0, relief='ridge',
			geom=self.set_geom(row=0, column=0, padx=res.sx(2), freeze=1)
		)
		self.timeLabel = self.new_Label(
			self.clockFrame, font=('arial', res.sy(16)), bg=self.col['perf frm'], fg=self.col['timer fg'],
			geom=self.set_geom(row=1, column=0)
		)

		self.livesFrame = self.new_Frame(
			self.perfWindow, width=res.sx(396), height=res.sy(94), bg=self.col['perf frm'],
			geom=self.set_geom(row=1, column=0, padx=res.sx(2), columnspan=2, freeze=1)
		)

		self.livesLabel = self.new_Label(
			self.livesFrame, bg=self.col['perf frm'], fg=self.col['lives fg'], font=('arial', res.sy(20)),
			geom=self.set_geom(row=0, column=0, padx=res.sx(70), pady=res.sy(28), hidden=1)
		)

		self.progressLabel = self.new_Label(
			self.livesFrame, text='Progress: ', bg=self.col['perf frm'], fg=self.col['lives fg'],
			font=('arial', res.sy(20)), anchor='w',
			geom=self.set_geom(row=0, column=0, padx=res.sx(50), pady=res.sy(28), hidden=1)
		)

		self.statsFrame = self.new_Frame(
			self.perfWindow, width=res.sx(396), height=res.sy(278), bg=self.col['perf frm'],
			geom=self.set_geom(row=2, column=0, pady=res.sy(2), columnspan=2, freeze=1)
		)

		self.correctFrame = self.new_Frame(
			self.statsFrame, bg=self.col['perf frm'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(10), pady=res.sy(5), sticky='w')
		)
		self.correctTitle = self.new_Label(
			self.correctFrame, text='Correct:', font=('arial', res.sy(18)),
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(3), sticky='w')
		)
		self.correctCounterLabel = self.new_Label(
			self.correctFrame, text='0', font=('arial', res.sy(20)), width=7, anchor='e',
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=1, column=0)
		)


		self.wrongFrame = self.new_Frame(
			self.statsFrame, bg=self.col['perf frm'],
			geom=self.set_geom(row=1, column=0, padx=res.sx(10), pady=res.sy(5), sticky='w')
		)
		self.wrongTitle = self.new_Label(
			self.wrongFrame, text='Wrong:', font=('arial', res.sy(18)),
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(3), sticky='w')
		)
		self.wrongCounterLabel = self.new_Label(
			self.wrongFrame, text='0', font=('arial', res.sy(20)), width=7, anchor='e',
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=1, column=0)
		)

		self.totalFrame = self.new_Frame(
			self.statsFrame, bg=self.col['perf frm'],
			geom=self.set_geom(row=2, column=0, padx=res.sx(10), pady=res.sy(5), sticky='w')
		)
		self.totalTitle = self.new_Label(
			self.totalFrame, text='Total:', font=('arial', res.sy(18)),
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(3), pady=res.sy(3), sticky='w')
		)
		self.totalCounterLabel = self.new_Label(
			self.totalFrame, text='0', font=('arial', res.sy(20)), width=7, anchor='e',
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=1, column=0)
		)

		self.accuracyFrame = self.new_Frame(
			self.statsFrame, bg=self.col['perf frm'],
			geom=self.set_geom(row=1, column=1, rowspan=2, padx=res.sx(15))
		)
		self.accuracyTitle = self.new_Label(
			self.accuracyFrame, text='Accuracy:', font=('arial', res.sy(20)), anchor='s',
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=0, column=0, padx=res.sx(50), pady=res.sy(10), ipady=res.sy(35))
		)
		self.accuracyCounterLabel = self.new_Label(
			self.accuracyFrame, text='0.00 %', font=('arial', res.sy(28)),
			bg=self.col['perf frm'], fg=self.col['stats fg'],
			geom=self.set_geom(row=1, column=0, sticky='e')
		)



	def start_new_game(self, allKanji, **kwargs):
		'''
		required arguments:
			1) Dictionary of kanji as keys and answers as values
			2) Mode of gameplay (currently supports 'vocab' and 'writing')
			3) all the difficulty settings of the game: lives, time, recovery, repetition
			4) language settings (only applies if mode is set to 'vocab')
		'''
		self.choices = [kanji for kanji in allKanji]
		self.originalChoices = self.choices
		self.answers = {}
		self.answers = {}
		for kanji in allKanji:
			answers = allKanji[kanji]
			self.answers[kanji] = self.check_for_katakana(answers)

		self.usedChoices = []

		self.gamemode = kwargs['gamemode']
		
		self.maxTime = kwargs['difficulties']['time']
		self.maxLives = kwargs['difficulties']['lives']

		self.recovery = kwargs['difficulties']['recover']

		self.repetition = len(self.choices) - kwargs['difficulties']['repetition']

		self.language = kwargs['language']

		if self.gamemode == 'vocab':
			self.setup_vocab_game()

		else:
			self.setup_writing_game(kwargs['showkana'])

		self.gameRunning = False
		self.exitInvoke = kwargs['invoke_exit'] if 'invoke_exit' in kwargs else self.null

	def check_for_katakana(self, answers): #checks if the vocab answer input matches any katakana answers
		answer = {}
		for kana in answers:
			if kana[0] in translator.katakanaToHiraganaDict:
				hiragana = ''.join([translator.katakanaToHiraganaDict[katakana] for katakana in kana])
				answer[hiragana] = answers[kana]
			else:
				answer[kana] = answers[kana]

		return answer

	def setup_vocab_game(self, **kwargs):
		self.timeLeft = self.maxTime
		self.lives = self.maxLives

		if 'overwritechoices' in kwargs:
			self.choices = kwargs['overwritechoices']
			self.repetition = len(self.choices)

		self.answerMessageLabel.config(text = 'Press enter to begin')
		self.load_widgets(self.submitVocabEntry, self.flashcardLabel, self.livesLabel)
		self.submitVocabEntry.focus_set()
		self.submitVocabEntry.bind('<Return>', self.initiate_vocab_countdown)

		self.correct, self.wrong, self.total, self.accuracy, self.streak = 0, 0, 0, 0, 0
		self.mistakes = []

		self.currentLanguage = 'jap' if self.language == 'both' else self.language
		if self.language == 'eng':
			self.translator.change_language('ABC')

		self.livesLabel.config(text = f'Lives: {self.lives}')

		self.draw_idle_meters()

	def reveal_kana(self, *args):
		self.showKanaButton.config(state = DISABLED)
		self.kanaLabel.config(text = args[0])

	def initiate_vocab_countdown(self, *args):
		self.answerMessageLabel.config(text = '')
		self.submitVocabEntry.unbind('<Return>')
		self.submitVocabEntry.delete(0, END)
		self.countdown_to_start()

	def setup_writing_game(self, showkana, **kwargs):
		self.showKana = showkana
		if self.showKana is False:
			self.load_widgets(self.showKanaButton)
			self.kanaLabel.config(anchor = 'w')

		if 'overwritechoices' in kwargs:
			self.choices = kwargs['overwritechoices']
			self.repetition = len(self.choices)

		self.answerMessageLabel.config(text = 'Click to begin')
		self.load_widgets(self.checkKanjiLabel, self.startWritingButton, self.kanaFrame, self.kanaLabel, self.englishFrame, self.englishLabel, self.progressLabel)

		self.correct, self.wrong, self.total, self.accuracy, self.streak = 0, 0, 0, 0, 0
		self.mistakes = []

		allChoicesNum = len(self.choices)
		self.progressLabel.config(text = f'Progress: 0 / {allChoicesNum}')

	def countdown_to_start(self):
		time = 1500 #ms
		cycles = 3 #number of countdowns before game starts
		cycleperiod = time // cycles #time in ms per cycle
		self.flashcardLabel.config(text = cycles, fg = '#ffffff')

		def countdown(time, maxtime, cycleperiod, FPS):
			frameTime = 1000 // FPS #get the time allocated per frame. 1000 is the numerator as 1000 ms = 1 second
			if time % cycleperiod < frameTime:
				self.flashcardLabel.config(text = (time // cycleperiod))

			self.configure_clock_angle(angle = int(360 * (maxtime - time) / maxtime))
			time -= frameTime
			if time > 0:
				self.root.after(frameTime, lambda: countdown(time, maxtime, cycleperiod, FPS))

			else:
				self.start_vocab_game()

		self.root.after(1, lambda: countdown(time, time, cycleperiod, self.FPS))

	def draw_idle_meters(self):
		#timer: tl = topleft, br = bottomright, tns = ring thickness
		tl_x, tl_y, br_x, br_y, tns = 20, 20, 120, 120, 5
		self.clockRing = self.clockCanvas.create_oval(tl_x, tl_y, br_x, br_y, fill = '#d3eac8')
		self.clockFiller = self.clockCanvas.create_oval(tl_x + tns, tl_y + tns, br_x - tns, br_y - tns, fill = '#000000')
		self.clockArc = self.clockCanvas.create_arc(tl_x + tns, tl_y + tns, br_x - tns, br_y - tns , fill = self.col['timer fg'], start = 90, extent = 0)

		#life gague
		# self.gagueEdge = self.clockCanvas.create_rectangle(285, 15, 315, 225, fill = '#000000')
		# self.gagueFiller = self.clockCanvas.create_rectangle(290, 20, 310, 220, fill = '#111111')
		# self.gagueLevel = self.clockCanvas.create_rectangle(290, 220, 310, 220, fill = '#333333')

	def reset_meters(self):
		def wait_to_finish():
			self.clockCanvas.delete(self.clockArc)
			self.timeLabel.config(text = '')

		self.root.after(1000 // self.FPS, wait_to_finish)

	def destory_meters(self):
		self.clockCanvas.delete(self.clockRing)
		self.clockCanvas.delete(self.clockFiller)

	def start_vocab_game(self):
		self.gameRunning = True
		self.root.after(1, self.run_timer)
		self.submitVocabEntry.bind('<Return>', self.submit_vocab_answer)
		if self.language == 'both':
			self.submitVocabEntry.bind('<space>', self.manual_change_language)
		self.answerMessageLabel.config(text = {'jap': 'あ', 'eng': 'ABC', 'both': 'あ*'}[self.language])
		self.get_new_flashcard()

	def start_writing_game(self):
		self.gameRunning = True
		self.unload_widgets(self.startWritingButton)
		self.load_widgets(self.checkWritingButton)
		self.get_new_flashcard()

	def submit_vocab_answer(self, *args):
		answer = self.submitVocabEntry.get()
		correct = self.check_vocab_answer(answer, self.currentLanguage)
		if correct is True:
			self.correct_vocab_submitted(answer)
			self.update_scoreboard(correct = 1)
		else:
			self.wrong_vocab_submitted(answer)
			self.update_scoreboard(wrong = 1)

		self.submitVocabEntry.delete(0, END)

	def check_writing_answer(self, *args):
		self.unload_widgets(self.checkWritingButton)
		self.load_widgets(self.checkWritingFrame, self.correctWritingButton, self.wrongWritingButton)
		self.checkKanjiLabel.config(text = self.chosenKanji)

		if self.showKana is False:
			self.kanaLabel.config(text = args[0])

	def tabulate_writing(self, correct):
		if correct is True:
			self.update_scoreboard(correct = 1)
		else:
			self.update_scoreboard(wrong = 1)
			self.record_mistakes('', self.chosenKanji)

		self.unload_widgets(self.checkWritingFrame, self.correctWritingButton, self.wrongWritingButton)
		self.load_widgets(self.checkWritingButton)
		self.checkKanjiLabel.config(text = '')
		self.progressLabel.config(text = f'Progress: {self.total} / {len(self.choices) + len(self.usedChoices)}')
		self.get_new_flashcard()

	def update_scoreboard(self, correct = 0, wrong = 0):
		self.correct += correct
		self.wrong += wrong
		self.total += 1
		self.accuracy = round(100 * self.correct / (self.total if self.total != 0 else 1), 2)
		accText = f"{self.accuracy}0 %" if str(self.accuracy)[::-1][1] == '.' else f"{self.accuracy} %"

		self.correctCounterLabel.config(text = self.correct)
		self.wrongCounterLabel.config(text = self.wrong)
		self.totalCounterLabel.config(text = self.total)
		self.accuracyCounterLabel.config(text = accText)

	def check_vocab_answer(self, inputanswer, language):
		if self.language == 'both':
			validAnswers = self.get_valid_answers(inputanswer, language)

		else:
			validAnswers = self.get_valid_single_answers(inputanswer, language)

		print(validAnswers, '<---- CORRECT ANSWERS')
		return (inputanswer in validAnswers)

	def get_valid_answers(self, inputanswer, language):
		if self.submissions.count(None) == 2:
			return self.get_valid_single_answers(inputanswer, language)
		elif language == 'eng':
			return self.get_reduced_english_answers(self.submissions[0])
		else:
			return self.get_reduced_japanese_answers(self.submissions[1])

	def get_reduced_english_answers(self, firstanswer):
		answers = self.answers[self.chosenKanji]
		if firstanswer in answers:
			return answers[firstanswer]
		else:
			for answer in answers:
				if '(' in answer and firstanswer in ''.join(kana for kana in answer if not (kana in '()')):
					return answers[answer]

	def get_reduced_japanese_answers(self, firstanswer):
		reducedanswer = []
		answers = self.answers[self.chosenKanji]
		for answer in answers:
			if firstanswer in answers[answer] and not ('(' in answer):
				reducedanswer.append(answer)
			elif firstanswer in answers[answer] and ('(' in answer):
				reducedanswer.append(''.join(char for char in answer if not (char in '()')))
				reducedanswer.append(answer[answer.index('(') + 1:answer.index(')')])

		return reducedanswer

	def get_valid_single_answers(self, inputanswer, language):
		answers = self.answers[self.chosenKanji]
		if language == 'jap':
			answer = []
			for kana in answers:
				if not ('(' in kana):
					answer.append(kana)
				else:
					answer.append(''.join(char for char in kana if not (char in '()')))
					answer.append(kana[kana.index('(') + 1:kana.index(')')])
	
			return answer
		else:
			return [a for b in [answers[answer] for answer in answers] for a in b]

	def get_new_flashcard(self):
		if self.gamemode == 'vocab':
			self.get_new_vocab_flashcard()

		elif self.gamemode == 'writing':
			self.get_new_writing_flashcard()

	def get_new_vocab_flashcard(self):
		self.chosenKanji = self.choose_kanji()
		self.display_details(self.gamemode, self.chosenKanji)
		self.submissions = self.get_new_submissions()

	def get_new_writing_flashcard(self):
		self.chosenKanji = self.choose_kanji()
		self.display_details(self.gamemode, self.chosenKanji)

	def get_new_submissions(self):
		if self.language == 'both':
			submissions = [None, None]
		else:
			submissions = []

		return submissions

	def choose_kanji(self):
		if len(self.usedChoices) == self.repetition or self.repetition == 0:
			self.reset_choices()
		kanji = choice(self.choices)
		self.choices.remove(kanji)
		self.usedChoices.append(kanji)
		return kanji

	def display_details(self, gamemode, kanji):
		if gamemode == 'vocab':
			self.display_vocab_details(kanji)
		elif gamemode == 'writing':
			self.display_writing_details(kanji)
		#else: in case new gamemodes are introduced.

	def display_vocab_details(self, kanji):
		fg = {1: '#ffffff', 2: '#99ff99', 3: '#99ffff', 4: '#d9b3ff', 5: '#ffd9b3'}[len(kanji)]
		self.flashcardLabel.config(text = kanji, fg = fg)

	def display_writing_details(self, kanji):
		self.answerMessageLabel.config(text = 'Draw the kanji')
		answers = self.answers[kanji]
		kanaText, englishText = '', ''
		for num, kana in enumerate(answers, start = 1):
			excess = ', \n' if (num % 3 == 0) else ', '
			kanaText += kana + (excess)
			englishText += f"{', '.join(self.calculate_length(answers[kana]))}\n\n"
		kanaText = kanaText.rstrip(excess)
		self.englishLabel.config(text = englishText)
		if self.showKana is True:
			self.kanaLabel.config(text = kanaText)
		else:
			self.kanaLabel.config(text = '')
			self.showKanaButton.config(state = NORMAL, command = lambda: self.reveal_kana(kanaText))
			self.checkWritingButton.config(command = lambda: self.check_writing_answer(kanaText))

	def calculate_length(self, englishlist):
		textLengthSpan = 30
		fullString = ''.join(englishlist)
		if len(fullString) <= textLengthSpan:
			return englishlist
		else:
			cumulativeLength = 0
			editedList = []
			for english in englishlist:
				cumulativeLength += len(english)
				if cumulativeLength <= textLengthSpan:
					editedList.append(english)
				else:
					editedList.append(f"\n{english}")
					cumulativeLength = 0
			return editedList

	def reset_choices(self):
		for kanji in self.usedChoices:
			self.choices.append(kanji)
		self.usedChoices.clear()

	def correct_vocab_submitted(self, inputanswer):
		print('CORRECT\n')
		if self.language == 'both':
			self.add_to_timer(self.recovery / 2)
			self.check_submitted_answers(inputanswer)

		else:
			self.add_to_timer(self.recovery)
			self.manage_submissions(inputanswer)
			self.update_records(self.submissions)
			self.get_new_flashcard()

	def wrong_vocab_submitted(self, inputanswer):
		print('WRONG\n')
		gameOver = self.deduct_life()
		self.record_mistakes(inputanswer, self.chosenKanji)
		if gameOver is False:
			self.reset_timer()
			self.manage_submissions(inputanswer)
			self.update_records(self.submissions)
			self.get_new_flashcard()
			self.change_language(language = 'jap')

	def manage_submissions(self, answer):
		if self.language == 'both':
			self.submissions[0 if self.currentLanguage == 'jap' else 1] = answer
			if None in self.submissions:
				self.submissions[self.submissions.index(None)] = '_UNANSWERED_'
		else:
			self.submissions.append(answer)

	def check_submitted_answers(self, inputanswer):
		self.submissions[0 if self.currentLanguage == 'jap' else 1] = inputanswer
		if not (None in self.submissions):
			self.update_records(self.submissions)
			self.get_new_flashcard()
			self.change_language(language = 'jap')

		else:
			self.change_language(language = 'jap' if self.currentLanguage == 'eng' else 'eng')

	def manual_change_language(self, *args):
		if (self.submitVocabEntry.get() == '') and (self.submissions.count(None) == 2):

			def wait_to_delete():
				self.submitVocabEntry.delete(0, END)

			self.submitVocabEntry.after(1, wait_to_delete)
			self.change_language(language = 'jap' if self.currentLanguage == 'eng' else 'eng')

	def change_language(self, language):
		self.currentLanguage = language
		language = 'あ' if self.currentLanguage == 'jap' else 'ABC'
		text = f'{language}*' if (self.submissions.count(None) == 2) else language
		self.answerMessageLabel.config(text = text)
		self.translator.change_language(language)

	def run_timer(self):
		self.timeLeft -= 1 / self.FPS
		self.update_time_left()

		if self.gameRunning is True:
			self.root.after(1000 // self.FPS, self.run_timer)

		if self.timeLeft <= 0:
			self.time_up()

		elif self.timeLeft >= self.maxTime:
			self.reset_timer()

	def time_up(self):
		gameOver = self.deduct_life()
		self.reset_timer()
		if gameOver is False:
			if self.language == 'both' and self.submissions.count(None) == 2:
				self.submissions[1 if self.currentLanguage == 'eng' else 0] = '_UNANSWERED_'
				self.change_language(language = 'jap' if self.currentLanguage == 'eng' else 'eng')

			elif self.language == 'both' and self.submissions.count(None) == 1:
				self.get_new_flashcard()
				self.change_language(language = 'jap')

			else:
				self.get_new_flashcard()

	def deduct_life(self):
		self.lives -= 1
		self.livesLabel.config(text = f'Lives: {self.lives}')
		if self.lives == 0:
			self.game_over()
			return True
		return False

	def add_to_timer(self, amount):
		self.timeLeft += amount
		if self.timeLeft >= self.maxTime:
			self.reset_timer()

	def reset_timer(self):
		self.timeLeft = self.maxTime

	def update_time_left(self):
		timeString = str(round(self.timeLeft, 2))
		timeText = f'{timeString} s' if len(timeString[timeString.index('.') + 1:]) == 2 else f'{timeString}0 s'
		self.timeLabel.config(text = timeText if self.timeLeft > 0 else '0.00 s')
		self.configure_clock_angle(angle = int(360 * (1 - (self.maxTime - self.timeLeft) / self.maxTime)))

	def configure_clock_angle(self, angle):
		self.clockCanvas.delete(self.clockArc)
		self.clockArc = self.clockCanvas.create_arc(25, 25, 115, 115, fill = self.col['timer fg'], start = 90, extent = angle)

	def update_records(self, answers):
		pass

	def game_over(self):
		self.gameRunning = False
		if self.gamemode == 'vocab':
			self.vocab_game_over()

		elif self.gamemode == 'writing':
			self.writing_game_over()

		self.ready_mistakes()

	def ready_mistakes(self):
		if self.mistakes != []:
			self.load_widgets(self.practiceMistakesButton)

	def vocab_game_over(self):
		self.submitVocabEntry.delete(0, END)
		self.submitVocabEntry.unbind('<Return>')
		if self.language == 'both':
			self.submitVocabEntry.unbind('<space>')

		self.flashcardLabel.config(text = '')
		self.answerMessageLabel.config(text = 'Game over!')
		self.reset_meters()

		self.unload_widgets(self.submitVocabEntry)
		self.load_widgets(self.retryButton, self.returnButton, self.endButtonsFrame)

	def writing_game_over(self):
		self.answerMessageLabel.config(text = 'Game Over!')
		self.kanaLabel.config(text = '')
		self.englishLabel.config(text = '')
		self.checkKanjiLabel.config(text = '')
		self.unload_widgets(self.checkKanjiLabel, self.startWritingButton, self.kanaFrame, self.kanaLabel, self.englishFrame, self.englishLabel, 
							self.progressLabel, self.checkWritingFrame, self.correctWritingButton, self.wrongWritingButton, self.checkWritingButton)
		self.load_widgets(self.retryButton, self.returnButton, self.endButtonsFrame)

		if self.showKana is False:
			self.showKanaButton.config(state = DISABLED, command = None)
			self.unload_widgets(self.showKanaButton)

	def retry_game(self):
		self.reset_choices()
		self.reset_performance_interface()
		self.reset_mistakes()

		if len(self.choices) < len(self.originalChoices):
			self.choices = self.originalChoices

		if self.gamemode == 'vocab':
			self.unload_widgets(self.retryButton, self.returnButton, self.endButtonsFrame)
			self.load_widgets(self.submitVocabEntry)
			self.setup_vocab_game(overwritechoices = self.mistakes)
		elif self.gamemode == 'writing':
			self.unload_widgets(self.returnButton, self.returnButton, self.endButtonsFrame)
			self.load_widgets(self.startWritingButton)
			self.setup_writing_game(self.showKana)

	def exit_game(self):
		if self.gamemode == 'writing' and self.showKana is False:
			self.unload_widgets(self.showKanaButton)
		self.return_to_settings()

	def reset_performance_interface(self):
		self.correctCounterLabel.config(text = '0')
		self.wrongCounterLabel.config(text = '0')
		self.totalCounterLabel.config(text = '0')
		self.accuracyCounterLabel.config(text = '0.00 %')

	def reset_mistakes(self):
		self.hide_mistake_details()
		for label in self.historyFrame.winfo_children():
			label.destroy()

		self.unload_widgets(self.practiceMistakesButton)

	def end_game(self):
		if self.gameRunning is True and self.gamemode == 'vocab':
			self.stop_running_vocab_game()

		elif self.gameRunning is False and self.gamemode == 'vocab':
			self.unload_widgets(self.submitVocabEntry)
			self.destory_meters()
			self.return_to_settings()

		elif self.gameRunning is True and self.gamemode == 'writing':
			self.stop_running_writing_game()

		else:
			self.unload_widgets(self.startWritingButton)
			if self.showKana is False:
				self.unload_widgets(self.showKanaButton)
			self.return_to_settings()

		self.gameRunning = False
		self.ready_mistakes()

	def stop_running_vocab_game(self):
		self.vocab_game_over()
		self.lives = 0
		self.livesLabel.config(text = 'Lives: 0')

	def stop_running_writing_game(self):
		self.writing_game_over()
		self.progressLabel.config(text = f'Progress: 0 / {len(self.choices) + 1}')

	def return_to_settings(self):
		self.answerMessageLabel.config(text = '')
		self.reset_performance_interface()
		self.unload_widgets(self.retryButton, self.returnButton, self.endButtonsFrame)
		self.exitInvoke(self)

	def record_mistakes(self, input_, current):
		num = len(self.historyFrame.winfo_children())
		label = Label(self.historyFrame, text = current[0], font = ('times', 30), bg = '#000000', fg = '#ff4444')
		padding = res.sy(3) if num % 2 == 0 else 0
		label.grid(row = num // 8, column = num % 8, padx = padding, pady = padding)

		label.bind('<Enter>', lambda *args, current = current, input_ = input_: self.display_mistake_details(current, input_))
		label.bind('<Leave>', self.hide_mistake_details)

		self.mistakes.append(current)

	def display_mistake_details(self, current, input_, *args):
		self.historyKanjiLabel.config(text = current)
		self.historyKanaLabel.config(text = ', '.join([kana for kana in self.answers[current]]))
		self.historyEnglishLabel.config(text = ', '.join([a for b in [self.answers[current][kana] for kana in self.answers[current]] for a in b]))
		self.historyInputLabel.config(text = input_)

	def hide_mistake_details(self, *args):
		self.historyKanjiLabel.config(text = '')
		self.historyKanaLabel.config(text = '')
		self.historyEnglishLabel.config(text = '')
		self.historyInputLabel.config(text = '')

	def practice_mistakes(self, mistakes):
		self.reset_choices()
		self.reset_performance_interface()
		self.reset_mistakes()
		del self.mistakes
		if self.gamemode == 'vocab':
			self.unload_widgets(self.retryButton, self.returnButton, self.endButtonsFrame)
			self.load_widgets(self.submitVocabEntry)
			self.setup_vocab_game(overwritechoices = mistakes)
		elif self.gamemode == 'writing':
			self.unload_widgets(self.returnButton, self.returnButton, self.endButtonsFrame)
			self.load_widgets(self.startWritingButton)
			self.setup_writing_game(self.showKana, overwritechoices = mistakes)

		self.unload_widgets(self.practiceMistakesButton)

def test():
	import config
	from utilities import decode

	root = Tk()
	root.geometry('1280x720')

	testInterface = Game_Interface(root, bg = '#555555')
	testInterface.load_window()

	rawdata = config.getData()[0][604:]
	truedata = {data[0]: decode(data[1]) for data in rawdata}

	testDifficulty = {'time': 50, 'lives': 3, 'recover': 2, 'repetition': 0}
	language = 'both'
	testMode = 'vocab'

	testInterface.start_new_game(truedata, gamemode = testMode, difficulties = testDifficulty, language = language, showkana = True)

	root.mainloop()

if __name__ == '__main__':
	test()