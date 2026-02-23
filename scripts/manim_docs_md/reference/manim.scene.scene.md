<!-- source: https://docs.manim.community/en/stable/reference/manim.scene.scene.html -->

# scene

Basic canvas for animations.

Type Aliases

class SceneInteractAction
:   ```python
    MethodWithArgs | 'SceneInteractContinue' | 'SceneInteractRerun'
    ```

Classes

|  |  |
| --- | --- |
| [`RerunSceneHandler`](manim.scene.scene.RerunSceneHandler.html#manim.scene.scene.RerunSceneHandler "manim.scene.scene.RerunSceneHandler") | A class to handle rerunning a Scene after the input file is modified. |
| [`Scene`](manim.scene.scene.Scene.html#manim.scene.scene.Scene "manim.scene.scene.Scene") | A Scene is the canvas of your animation. |
| [`SceneInteractContinue`](manim.scene.scene.SceneInteractContinue.html#manim.scene.scene.SceneInteractContinue "manim.scene.scene.SceneInteractContinue") | Object which, when encountered in `Scene.interact()`, triggers the end of the scene interaction, continuing with the rest of the animations, if any. |
| [`SceneInteractRerun`](manim.scene.scene.SceneInteractRerun.html#manim.scene.scene.SceneInteractRerun "manim.scene.scene.SceneInteractRerun") | Object which, when encountered in `Scene.interact()`, triggers the rerun of the scene. |
