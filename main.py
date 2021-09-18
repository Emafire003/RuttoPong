from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label


class PongPaddle(Widget):
    score = NumericProperty(0)
    # Potrebbe anzi caricarsi una barra
    bar_value = 0
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 5)#sposta la palla di un tot
            bounced = Vector(-1 * vx, vy)#gira la palla
            vel = bounced * 1.1 #aumenta la velocità
            ball.velocity = vel.x, vel.y + offset
            self.bar_value = self.bar_value + 1


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    temp_vx = NumericProperty(0)
    temp_vy = NumericProperty(0)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def burst(self):
        self.velocity_x = self.velocity_x*2
        self.velocity_y = self.velocity_y*2
        self.move()
        Clock.schedule_once(self.unburst, 1)

    def unburst(self, stuff):
        self.velocity_x = self.velocity_x / 2
        self.velocity_y = self.velocity_y / 2
        self.move()

    def freeze(self):
        self.temp_vx = self.velocity_x
        self.temp_vy = self.velocity_y
        self.velocity_x = 0
        self.velocity_y = 0
        Clock.schedule_once(self.unfreeze, 0.6)

    def unfreeze(self, stuff):
        self.velocity_x = self.temp_vx
        self.velocity_y = self.velocity_y

class ProgBar(BoxLayout):
    pass

class LabelChanging(Label):
    color_number = 0
    color_number_max = 0
    color_list = ["#6a0a83"]
    backward_repeat: True #True, rifà la lista all'indietro
    changing_interval = 0.16
    direction: True #True 0 to max, false max to 0
    
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

    #Changes the color of the text
    def change_color(self, stuff):

        #Checks if the repeat is true, and then if the direction is up or down
        if (self.backward_repeat and not self.direction):
            self.color_number = self.color_number - 1
            if(self.color_number < 0):
                self.direction = True
                self.color_number = 0
        else:
            self.color_number = self.color_number + 1

        #Checks if the number is more than max and if it is repeat mode sets to max and direction false, if not sets to 0
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
    bgm = SoundLoader.load('background.wav')
    burst_cost = 5
    freeze_cost = 6
    music = True
    winning = True
    winat = 10

    def menu(self):
        Clock.schedule_interval(self.backgroundplay, 32)
        Clock.schedule_once(self.backgroundplay, 1)

    def burst_ballSX(self):
        if(self.player1.bar_value >= self.burst_cost):
            self.ball.burst()
            self.player1.bar_value = self.player1.bar_value - self.burst_cost
        else:
            print("non abbastanza punti")

    def burst_ballDX(self):
        if(self.player2.bar_value >= self.burst_cost):
            self.ball.burst()
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

    def play_sound(self, file, volume):
        sound = SoundLoader.load(file)
        if sound:
            print("Sound found at %s" % sound.source)
            print("Sound is %.3f seconds" % sound.length)
            sound.volume= volume
            sound.play()

    def backgroundplay(self, something):
        if(self.music == False):
            return
        if self.bgm:
            print("Sound found at %s" % self.bgm.source)
            print("Sound is %.3f seconds" % self.bgm.length)
            self.bgm.volume= 0.1
            self.bgm.play()
        print("restarted song")

    def backgroundstop(self, something):

        if self.bgm:
            print("Sound found at %s" % self.bgm.source)
            print("Sound is %.3f seconds" % self.bgm.length)
            self.bgm.volume= 0.1
            self.bgm.stop()
            print("stopped song")

    def toggle_winning(self):
        if (self.winning):
            self.winning = False
        else:
            self.winning = True

    def toggle_music(self):
        if(self.music):
            self.music = False
            self.backgroundstop("hi")
        else:
            self.music = True
            self.backgroundplay("hi")

    def set_pause(self):
        self.pause = True
        self.ball

    def set_unpause(self):
        self.pause = False

    def update_texts(self):
        self.ids.points_sx.text = str(self.player1.bar_value)
        self.ids.points_dx.text = str(self.player2.bar_value)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel
        print("Serving Ball")

    #Main method della classe, aggiorna ogni 60esimo di secondo il gioco. fa muovere la palla ecc
    def update(self, dt):
        if(not self.pause):

            if (self.winning):
                if(self.player1.score >= self.winat):
                    self.serve_ball(vel=(0, 0))
                    print("YAAAAY PLAYER ONE WON")
                    #self.play_sound("winner")
                    #WinnerPopup
                    #Set score to 0
                    """On close of the winner popup start the game all over again"""
                if (self.player2.score >= self.winat):
                    self.serve_ball(vel=(0, 0))
                    print("YAAAAY PLAYER TWO WON")
                    # self.play_sound("winner")
                    # WinnerPopup
                    # Set score to 0
                    """On close of the winner popup start the game all over again"""
            self.ball.move()

            # bounce of paddles
            self.player1.bounce_ball(self.ball)
            self.player2.bounce_ball(self.ball)

            #Updating text points
            self.update_texts()

            # Se la y della palla è a 0 (pavimento) o all'aletzza della classe ponggame ovvere l'altezza della finestra
            # inverti la direzione della velocità y
            if (self.ball.y < self.y) or (self.ball.top > self.top):
                self.ball.velocity_y *= -1

            # went of to a side to score point?
            if self.ball.x < self.x:
                self.player2.score += 1
                self.serve_ball(vel=(4, 0))
                self.play_sound('punto.wav', 1)
                print("PUNTO SX")
            if self.ball.x > self.width:
                self.player1.score += 1
                self.serve_ball(vel=(-4, 0))
                self.play_sound('punto.wav', 1)
                print("PUNTO DX")

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y




class PongApp(App):

    def load_fonts(self):
        print("Registering fonts...")
        LabelBase.register(name='Karantina_Regular',
                           fn_regular='data/fonts/Karantina-Regular.ttf', fn_bold='data/fonts/Karantina-Bold.ttf')
        """LabelBase.register(name='Karantina_Bold',
                           fn_regular='data/fonts/Karantina-Bold.ttf')"""
        LabelBase.register(name='Karantina_Light',
                           fn_regular='data/fonts/Karantina-Light.ttf')
        print("Registered Fonts!")

    def build(self):
        self.load_fonts()
        game = PongGame()
        game.menu()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
