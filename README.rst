PySPG is a set of python classes aimed to those of you that must (or wish to)
run programs in which some parameters change.

For example: Let's suppose you want to run simulations in which three
parameters are involved, let's say D, k, a. These are some possible scenarios

You want to run a simulation in which D, k are kept fixed while a linearly
changes between (eeeer...) 0 and 5 with a step of 0.2. It's really easy: in the
language of your choice you write a program that performs the simulation and
before and after the important part of a simulation, you just add a loop on the
a variable. Now you are done But after that, you want to keep fixed D. Now both
k and a vary linearly between 0 and 5 with a step of 0.2. It's easy once again:
you just add an external loop on the k variable. And you're done again. But
note that you had to recompile your code without changing the important part of
your code: The simulation.

After those simulations you realise that the scale relevant for the variable a
is not a linear one, but logarithmic. Although the change is easy, you must
recompile.  And if you want to run a simulation in which the variation is on D
variable? Obviously compile the whole thing again...
And if the variation must be exponential???
...

Well, perhaps you do not have to recompile if you program in an interpreted
language. But what you are doing is touch on, and on, and on again your source
code. The probability of doing something weird increases.

The only relevant information your program returns is the measures for each
parameter set. The parameter variation is something subsidiary of the main
point of the program, that is performing measures. The values of the variables
can be set from outside. And this is the point of PySPG.

With PySPG you can extract one layer of complexity from your compiled code. For
long simulations, is obvious that the time your program takes to run is NOT in
the loops of changing parameters. In this way, you can avoid the problem of
writing boring code and just write a simple text file that will launch the
other program for you.

PySPG generates a directory hierarchy that allows you to easily navigate your
data.

Is it all?

No. Although not so well documented yet, PySPG also features a generator of
plots for your simulations. It can automatically generate 2D-plots in the
format of Grace, and for a future version, a 3D utility is planned. Also an
automatic report generator (TeX-based) is half-done. And it is GPL'd, so you
can extend it as much as you wish.

