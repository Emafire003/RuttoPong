from kivy.app import App
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button


class PongPaddle(Widget):
    score = NumericProperty(0)
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 5)#sposta la palla di un tot
            bounced = Vector(-1 * vx, vy)#gira la palla
            vel = bounced * 1.1 #aumenta la velocità
            ball.velocity = vel.x, vel.y + offset
            print("COLLIDED")


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


class OptionsDropDown(DropDown):
    pass

class MusicButton(Button):

    def change_text(self, text):
       self.text = text


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    pause = False
    bgm = SoundLoader.load('background.wav')
    #dropdown = OptionsDropDown()

    def spawn_dropdown(self):
        dropdown = DropDown()
        for index in range(10):
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.

            btn = Button(text='Value %d' % index, size_hint_y=None, height=44)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))

            # then add the button inside the dropdown
            dropdown.add_widget(btn)

        # create a big main button
        mainbutton = Button(text='Hello', size_hint=(None, None))

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        mainbutton.bind(on_release=dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        """mainbutton = self.ids.options_button
        mainbutton.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.ids.options_button, 'Test', x))"""

    def remove_dropdown(self):
        self.dropdown.dismiss()

    def menu(self):
        Clock.schedule_interval(self.backgroundplay, 32)
        Clock.schedule_once(self.backgroundplay, 1)

    def play_sound(self, file, volume):
        sound = SoundLoader.load(file)
        if sound:
            print("Sound found at %s" % sound.source)
            print("Sound is %.3f seconds" % sound.length)
            sound.volume= volume
            sound.play()

    def backgroundplay(self, something):

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

    def set_pause(self):
        self.pause = True
        self.backgroundstop("h")

    def set_unpause(self):
        self.pause = False
        self.backgroundplay("h")

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel
        print("Serving Ball")

    def update(self, dt):
        if(not self.pause):
            self.ball.move()

            # bounce of paddles
            self.player1.bounce_ball(self.ball)
            self.player2.bounce_ball(self.ball)

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
    def build(self):
        game = PongGame()
        game.menu()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
