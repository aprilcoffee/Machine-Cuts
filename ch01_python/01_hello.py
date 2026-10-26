"""ch01-01 - Your first script

Open this file in VS Code and press the triangle at the top right
(Run Python File). The output appears in the terminal at the bottom.

Or type it yourself in that terminal:

    python ch01_python/01_hello.py

Everything after a # is a comment: Python ignores it, humans read it.
"""

# print() writes something into the terminal
print("hello, machine cut")

# a variable is a name for a value
fps = 25                 # frames per second
minutes = 10             # length of a film

# Python does the arithmetic for you
seconds = minutes * 60
frames = seconds * fps
print("a", minutes, "minute film at", fps, "fps has", frames, "frames")

# an f-string puts variables into text: f"... {name} ..."
print(f"that is {frames} still images, one after another")

# a list holds several values; a for loop visits them one by one
rates = [24, 25, 30, 60]
for rate in rates:
    print(f"  at {rate} fps: {minutes * 60 * rate} frames")

# if / else: decide something
if frames > 10000:
    print("too many for a human to look at one by one.")
else:
    print("you could look at every one of them.")

print("\nNow change `minutes` at the top to 90 and press Run again.")
