from cdktf import App
from class_just_modules import StackJustModules
from class_just_provider import StackJustProvider

app = App()
StackJustModules(app, "just_modules")
StackJustProvider(app, "just_provider")

app.synth()
