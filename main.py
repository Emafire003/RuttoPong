from kivy.app import App
from kivy.lang import Builder
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

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    button = Button()

    def menu(self):
        self.button = ObjectProperty(None)
        self.button = Button(text="Avvio", font_size=16, size=(110, 40), size_hint=(1,1), pos=self.center, background_color="cyan")
        self.button.bind(on_press=self.serve_ball)
        self.add_widget(self.button)

    def play_sound(self, file):
        sound = SoundLoader.load(file)
        if sound:
            print("Sound found at %s" % sound.source)
            print("Sound is %.3f seconds" % sound.length)
            sound.play()
    def serve_ball(self, vel=(4, 0)):
        self.remove_widget(self.button)
        self.ball.center = self.center
        vel = (4,0)
        self.ball.velocity = vel
        print("Serving Ball")

    def update(self, dt):
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
            self.play_sound('punto.wav')
            print("PUNTO SX")
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))
            self.play_sound('punto.wav')
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


