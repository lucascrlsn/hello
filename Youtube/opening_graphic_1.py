
import turtle as tu

# for escape key exit function see: https://stackoverflow.com/questions/50733662/how-to-continue-or-exit-the-program-by-pressing-keys

foo = tu.Turtle()
foo.left(90)
foo.speed(5000)
foo.hideturtle()



# recursion
def draw(l):
    if l < 3:
        return
    else:
        # use next var for scaling factors
        scaling_factor = l / 2
        # scaling_factor = 3*l / 4
        foo.forward(l)
        foo.left(30)
        draw(scaling_factor)
        foo.right(60)
        draw(scaling_factor)
        foo.left(30)
        foo.backward(l)



draw(100)
