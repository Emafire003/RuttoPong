import sys

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
import os
from kivy.utils import platform
from kivy.uix.switch import Switch

# TODO ostacoli bottone (tipo costo 7/8)
# TODO On a win,usare delle gif di coriandoli o robe del genere e fare un'animation con direzione e size randomizzate


class PathFinder:
    app_folder = "."

    def __init__(self):
        self.app_folder = "."

    def get_path(self):
        try:
            if platform == "android":
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                self.app_folder = os.path.dirname(os.path.abspath(__file__))
            elif platform == "win":
                try:
                    # PyInstaller creates a temp folder and stores path in _MEIPASS
                    self.app_folder = sys._MEIPASS
                except Exception:
                    self.app_folder = os.path.abspath(".")
        except Exception as e:
            self.app_folder = os.path.abspath(".")
            print(e)
        print(self.app_folder)
        return str(self.app_folder)


class PongPaddle(Widget):
    score = NumericProperty(0)
    # Potrebbe anzi caricarsi una barra
    max_power_points = 10
    bar_value = 0
    pathfinder = PathFinder()

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 5)  # sposta la palla di un tot
            bounced = Vector(-1 * vx, vy)  # gira la palla
            vel = bounced * 1.1   # aumenta la velocità
            ball.velocity = vel.x, vel.y + offset
            if(self.bar_value < self.max_power_points):
                self.bar_value = self.bar_value + 1
            # Easy fix for the super launchery thing
            # Make the ball invulnerable to vel changes for a short period of time


class PongBall(Widget):
    pathfinder = PathFinder()
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    temp_vx = NumericProperty(0)
    temp_vy = NumericProperty(0)
    temp_vel = (0, 0)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def pause(self):
        self.temp_vx = self.velocity_x
        self.temp_vy = self.velocity_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity = (0, 0)

    def unpause(self):
        self.velocity_x = self.temp_vx
        self.velocity_y = self.temp_vy

    def burst(self):
        # Questo if serve perché se ci sono un burst e un freeze simultanei dopo la velocità riprenderebbe a 0
        """if(self.temp_vy == -1 and self.temp_vx == -1):
            self.temp_vx = self.velocity_x
            self.temp_vy = self.velocity_y"""
        self.velocity_x = self.velocity_x*2
        self.velocity_y = self.velocity_y*2
        self.move()
        Clock.schedule_once(self.unburst, 1)

    def unburst(self, stuff):
        self.velocity_x = self.velocity_x/2
        self.velocity_y = self.velocity_y/2
        """self.temp_vy = -1
        self.temp_vx = -1"""
        self.move()

    def freeze(self):
        # if (self.temp_vy == -1 and self.temp_vx == -1):
        self.temp_vx = self.velocity_x
        self.temp_vy = self.velocity_y
        self.velocity_x = 0
        self.velocity_y = 0
        Clock.schedule_once(self.unfreeze, 0.6)

    def unfreeze(self, stuff):
        self.velocity_x = self.temp_vx
        self.velocity_y = self.temp_vy
        self.temp_vy = -1
        self.temp_vx = -1


class LabelChanging(Label):
    color_number = 0
    color_number_max = 0
    color_list = ["#6a0a83"]
    backward_repeat: True  # True, rifà la lista all'indietro
    changing_interval = 0.16
    direction: True  # True 0 to max, false max to 0
    
    def __init__(self, **kwargs):
        super(LabelChanging, self).__init__()
        self.backward_repeat = True
        self.direction = True
        self.color_list = ["#6a0a83"]
        self.color_number = 0
        self.color_number_max = 0
        self.changing_interval = 0.16
        Clock.schedule_once(self.start_changing, 0.1)

    def set_color_list(self, list):
        self.color_number_max = len(list)
        self.color_list = list

    # Changes the color of the text
    def change_color(self, stuff):

        # Checks if the repeat is true, and then if the direction is up or down
        if (self.backward_repeat and not self.direction):
            self.color_number = self.color_number - 1
            if(self.color_number < 0):
                self.direction = True
                self.color_number = 0
        else:
            self.color_number = self.color_number + 1

        # Checks if the number is more than max and if it is repeat mode sets to max and direction false,
        # if not sets to 0
        if(self.color_number > self.color_number_max):
            if(self.backward_repeat):
                self.direction = False
                self.color_number = self.color_number_max
            else:
                self.color_number = 0
        self.color = self.color_list[self.color_number]

    def start_changing(self, stuff):
        Clock.schedule_interval(self.change_color, self.changing_interval)


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    pause = False
    pathfinder = PathFinder()
    path = pathfinder.get_path()

    burst_cost = 5
    freeze_cost = 6
    music = True
    winning = True
    winat = 10
    winner = "0"
    seffects = True
    music_volume = 0.1
    sound_volume = 1
    sounds = {"rup": SoundLoader.load(path+'/data/sounds/rup.wav'),
              "punto": SoundLoader.load(path+'/data/sounds/punto.wav'),
              "burst": SoundLoader.load(path+'/data/sounds/burst.wav'),
              "bgm": SoundLoader.load(path + '/data/sounds/background.wav'),
              "winner": SoundLoader.load(path + '/data/sounds/winner.wav')}

    # Mettere il max power points nelle opzioni TODO
    def menu(self):
        Clock.schedule_once(self.backgroundplay, 1)
        Clock.schedule_interval(self.backgroundplay, 33.8) # DEVE stare DOPO il primo coso che la fa partire
        
    def burst_ballSX(self):
        if(self.player1.bar_value >= self.burst_cost):
            self.ball.burst()
            self.play_sound(self.sounds["burst"], self.sound_volume)
            print("should be playing the sound?")
            self.player1.bar_value = self.player1.bar_value - self.burst_cost
        else:
            print("non abbastanza punti")

    def burst_ballDX(self):
        if(self.player2.bar_value >= self.burst_cost):
            self.ball.burst()
            self.play_sound(self.sounds["burst"], self.sound_volume)
            self.player2.bar_value = self.player2.bar_value - self.burst_cost
        else:
            print("non abbastanza punti")

    def freeze_ballSX(self):
        if(self.player1.bar_value >= self.freeze_cost):
            self.ball.freeze()
            self.player1.bar_value = self.player1.bar_value - self.freeze_cost
        else:
            print("non abbastanza punti")

    def freeze_ballDX(self):
        if(self.player2.bar_value >= self.freeze_cost):
            self.ball.freeze()
            self.player2.bar_value = self.player2.bar_value - self.freeze_cost
        else:
            print("non abbastanza punti")

    def play__sound(self, file, volume):
        sound = SoundLoader.load(self.pathfinder.get_path() + file)
        if sound and self.seffects:
            print("Sound found at %s" % sound.source)
            print("Sound is %.3f seconds" % sound.length)
            sound.volume = volume
            sound.play()

    def play_sound(self, sound, volume):
        if sound and self.seffects:
            print("Sound found at %s" % sound.source)
            print("Sound is %.3f seconds" % sound.length)
            sound.volume = volume
            sound.play()

    def backgroundplay(self, something):
        if(self.music is False):
            return
        if self.sounds["bgm"]:
            print("Sound found at %s" % self.sounds["bgm"].source)
            print("Sound is %.3f seconds" % self.sounds["bgm"].length)
            self.sounds["bgm"].volume = self.music_volume
            self.sounds["bgm"].play()
        print("restarted song")

    def backgroundstop(self, something):

        if self.sounds["bgm"]:
            print("Sound found at %s" % self.sounds["bgm"].source)
            print("Sound is %.3f seconds" % self.sounds["bgm"].length)
            self.sounds["bgm"].volume = self.music_volume
            self.sounds["bgm"].stop()
            print("stopped song")

    slider_temp_music = 0.1
    slider_temp_sound = 1
    check_slider = False

    def update_sliders(self):
        # Dovrebbe in teroia controllare una volta si e una no, e dovrebbe poter quindi usare il valore vecchio
        if (self.check_slider):
            self.slider_temp_music = self.ids.music_slider.value
            self.slider_temp_sound = self.ids.sound_slider.value
            self.check_slider = False
        else:
            self.check_slider = True
        if (self.music and self.slider_temp_music != self.ids.music_slider.value):
            self.music_volume = self.ids.music_slider.value / 100
            self.backgroundstop("hi")
            self.backgroundplay("hi1")
        if (self.seffects and self.slider_temp_sound != self.ids.sound_slider.value):
            self.sound_volume = self.ids.sound_slider.value / 100
            self.play_sound(self.sounds["burst"], self.ids.sound_slider.value / 100)
        return

    def update_inputs(self):

        # Controlla l'input del dropdown menu per i punti power e vittoria
        if(self.ids.winat_input.text.isdigit()):
            self.winat = int(self.ids.winat_input.text)
        else:
            self.ids.error_label1.text = "Error! Must be only numbers!"
            self.ids.error_label2.text = "Errore! Devono essere solo numeri!"
            self.ids.error_popup.open()

        # TODO restart function
        if (self.ids.max_power_points_input.text.isdigit()):
            self.player1.max_power_points = int(self.ids.max_power_points_input.text)
            self.player2.max_power_points = int(self.ids.max_power_points_input.text)
            if(self.player1.bar_value > self.player1.max_power_points):
                self.player1.bar_value = self.player1.max_power_points
            if (self.player2.bar_value > self.player2.max_power_points):
                self.player2.bar_value = self.player2.max_power_points
            self.ids.prog_sx.max = self.player1.max_power_points
            self.ids.prog_dx.max = self.player1.max_power_points
        else:
            self.ids.error_label1.text = "Error! Must be only numbers!"
            self.ids.error_label2.text = "Errore! Devono essere solo numeri!"
            self.ids.error_popup.open()

    def toggle_winning(self):
        if (self.winning):
            self.winning = False
        else:
            self.winning = True

    def toggle_seffects(self):
        if (self.seffects):
            self.seffects = False
        else:
            self.seffects = True

    def toggle_music(self):
        if(self.music):
            self.music = False
            self.backgroundstop("hi")
        else:
            self.music = True
            self.backgroundplay("hi")

    def set_pause(self):
        self.pause = True
        self.ball.pause()
        print("set pausing")

    def set_unpause(self):
        self.pause = False
        self.ball.unpause()
        print("set unpausing")

    # Updates the progress bar and the texts
    def update_texts(self):
        if(self.player1.bar_value <= self.player1.max_power_points):
            self.ids.points_sx.text = str(self.player1.bar_value)
            self.ids.prog_sx.value = self.player1.bar_value
        if(self.player2.bar_value <= self.player2.max_power_points):
            self.ids.points_dx.text = str(self.player2.bar_value)
            self.ids.prog_dx.value = self.player2.bar_value

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel
        print("Serving Ball")

    # Main method della classe, aggiorna ogni 60esimo di secondo il gioco. fa muovere la palla ecc
    def update(self, dt):
        # Updating volumes according to sliders
        self.update_sliders()
        # Updating text points
        self.update_texts()
        if(not self.pause):

            if (self.winning):
                if(self.player1.score >= self.winat):
                    self.serve_ball(vel=(0, 0))
                    print("YAAAAY PLAYER ONE WON")
                    self.set_pause()

                    self.play_sound(self.sounds["winner"], self.sound_volume)
                    self.winner = "1"
                    self.ids.winner_label.text = "Vince il giocatore 1!!!"
                    self.ids.winner_popup.open()

                    # Resetting the game
                    self.player1.score = 0
                    self.player2.score = 0
                    self.add_widget(self.ids.avvio)
                if (self.player2.score >= self.winat):
                    # Stopping bal
                    self.serve_ball(vel=(0, 0))
                    print("YAAAAY PLAYER TWO WON")
                    self.set_pause()
                    self.winner = "2"
                    self.ids.winner_label.text = "Vince il giocatore 2!!!"
                    self.ids.winner_popup.open()
                    self.play_sound(self.sounds["winner"], self.sound_volume)

                    # Resetting the game
                    self.player1.score = 0
                    self.player2.score = 0
                    self.add_widget(self.ids.avvio)

            self.ball.move()

            # bounce of paddles
            self.player1.bounce_ball(self.ball)
            self.player2.bounce_ball(self.ball)

            # Se la y della palla è a 0 (pavimento) o all'aletzza della classe ponggame ovvere l'altezza
            # della finestra
            # inverti la direzione della velocità y
            if (self.ball.y < self.y) or (self.ball.top > self.top):
                self.ball.velocity_y *= -1
                self.play_sound(self.sounds["rup"], self.sound_volume)
            # went of to a side to score point?
            if self.ball.x < self.x:
                self.player2.score += 1
                self.serve_ball(vel=(4, 0))
                print(self.pathfinder.get_path())
                self.play_sound(self.sounds["punto"], self.sound_volume)
            if self.ball.x > self.width:
                self.player1.score += 1
                self.serve_ball(vel=(-4, 0))
                self.play_sound(self.sounds["punto"], self.sound_volume)

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    pathfinder = PathFinder()
    path = pathfinder.get_path()

    def load_fonts(self):
        print("Registering fonts...")
        LabelBase.register(name='Karantina_Regular',
                           fn_regular=self.path + '/data/fonts/Karantina-Regular.ttf',
                           fn_bold=self.path + '/data/fonts/Karantina-Bold.ttf')
        LabelBase.register(name='Rubik',
                           fn_regular=self.path + '/data/fonts/Rubik-Regular.ttf',
                           fn_bold=self.path + '/data/fonts/Rubik-Bold.ttf',
                           fn_italic=self.path + '/data/fonts/Rubik-Italic.ttf',
                           fn_bolditalic=self.path + '/data/fonts/Rubik-BoldItalic.ttf')
        LabelBase.register(name='Karantina_Light',
                           fn_regular=self.path + '/data/fonts/Karantina-Light.ttf')
        LabelBase.register(name='Oswald',
                           fn_regular=self.path + '/data/fonts/Oswald-Regular.ttf',
                           fn_bold=self.path + '/data/fonts/Oswald-Bold.ttf')
        LabelBase.register(name='Oswald-Medium',
                           fn_regular=self.path + '/data/fonts/Oswald-Medium.ttf',
                           fn_bold=self.path + '/data/fonts/Oswald-SemiBold.ttf')
        LabelBase.register(name='Oswald-Light',
                           fn_regular=self.path + '/data/fonts/Oswald-ExtraLight.ttf',
                           fn_bold=self.path + '/data/fonts/Oswald-Light.ttf')
        print("Registered Fonts!")

    def build(self):
        self.load_fonts()
        game = PongGame()
        game.menu()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
