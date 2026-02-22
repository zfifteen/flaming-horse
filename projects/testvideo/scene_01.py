from manim import *
class Scene01(Scene):
    def construct(self):
        title = Text("Introduction")
        title.move_to(UP * 3.8)
        self.play(Write(title))
        self.wait(1)
