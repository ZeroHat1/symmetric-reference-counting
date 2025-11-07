# Symmetric Reference Counting (SRC)
A deterministic O(1) memory model without garbage collection.

*Author: [ZeroHat]*  
*Date: 2025-11-07*

### Introduction
When we talk about reference counting, everyone remembers one pain point: cyclic references.
This is when two objects refer to each other, and neither can be deleted, even though they are no longer referenced anywhere else.
A classic example:
```
a.link = b
b.link = a
del a
del b # ...but the memory is still allocated
```
Interpreters like CPython solve this with an additional “cycle collector” (cycle GC), but this is a different system, with graph traversal, unpredictable pauses, and additional overhead.
I wondered - why are these extra mechanisms needed at all?
If we consider everything as a system of related objects, then the scope is also an object.
It stores references to other objects, increasing their refcount.
And if the scope deletes a reference, it must also decrease the counter.
The classic model does not do this.
### Epiphany
The idea is simple:
the scope is also an object that participates in the reference count.
It is this “hole” that makes the classic RC imperfect:
it breaks its own rules.
If we fix this and treat everything, including Env, as a regular object with its own references,
then deleting a variable automatically leads to a correct decrease in the `refcount` of those it pointed to.
### Visualization
The problem with classic reference counting is that the model assumes the following structure:
each object in the heap references other objects, and the scope (or stack) simply “holds” references to them, but does not participate in the reference count itself.
The diagram below shows that each element of the heap is indeed pointed to by only one previous object,
but their reference counter is equal to 2 — one of the counted reference sources does not actually exist in the model.
That is, the model takes into account a “magical” external reference that is not formally described anywhere.
![](https://habrastorage.org/webt/z3/rx/2f/z3rx2fumzq7u2ldb1jaxifm7pdw.png)

The solution is to treat the scope itself as an object that owns references and participates in reference counting.
The scope (Env) now participates in the system as a regular object.hat owns the links and participates in the link count.
When a variable is removed from the scope must decrease the refcount
of the object it pointed to.
This is reflected in the diagram below:
![](https://habrastorage.org/webt/z-/ti/aa/z-tiaanymcarb-q_oaq4bdhyidu.png)

when a reference is removed from the stack, one of the real references to the object disappears,
and its reference count is correctly decreased.
Thus, the system becomes symmetrical:
the scope, objects, and connections between them all obey the same rules.
### Implementation example (Python pseudocode)
```
class Object:
	def __init__(self, name):
		self.refcount = 1
		self.ref = None
		self.name = name

	def link(self, ref):
		if self.ref != ref:
			self.ref = ref
			ref.refcount += 1

	def rc_dec(self):
		self.refcount -= 1

		if self.refcount <= 0:
			print(f"{self.name} deleted!")

	def delete(self):
		if self.ref:
			self.ref.rc_dec()
		self.rc_dec()

class Env:
	def __init__(self):
		self.objects = {}

	def new(self, name):
		self.objects[name] = Object(name)

	def get(self, name):
		return self.objects[name]

	def link(self, name, target_name):
		self.objects[name].link(self.objects[target_name])

	def delete(self, name):
		self.objects[name].delete()
		del self.objects[name]

	def print_rc(self):
		if len(self.objects) != 0:
			for obj in self.objects.values():
				print(f"RC {obj.name}: {obj.refcount}")
		else:
			print("Nothing!")
```

Test with a loop
```
env = Env()
env.new("a")
env.new("b")

env.link("a", "b")
env.link("b", "a")

env.delete("a")
env.delete("b")

env.print_rc()
```
Output:
```
a deleted!
b deleted!
```
- The loop has disappeared.
- The counters are zero.
- No graph traversals.
- Everything is O(1).

#### What actually happened
Objects symmetrically free references: both incoming and outgoing.
The scope (Env) now participates in the system as a regular object.
There are no more leaks, even with cycles and self-references.
The model is completely deterministic-deletion occurs exactly when the counter reaches zero.



Why this is not a “hack” but the completion of the model
Reference counting itself is not flawed-it is simply incomplete.
It assumes that there is some external agent (the scope) that can forget a reference without `DECREF`.
But if we consider everything as a closed system of objects, then no element has privileges. Everyone acts according to the same rules.
The result is a symmetric and self-contained reference system, where:
each object knows who it references;
when deleted, it correctly “unlinks” everyone, including itself;
no additional GC is needed.
### Experiments
Below are tests that include:
- regular chains a→b→c
- cycles a↔b
- self-references a→a

##### Unidirectional references
```
env = Env()

env.new("a")
env.new("b")

env.link("a", "b")  # a -> b

env.delete("a")
env.delete("b")

env.print_rc()
```
Result:
```
a deleted!
b deleted!
Nothing!
```
##### Cycle of two objects
```
env = Env()

env.new("a")
env.new("b")

env.link("a", "b")
env.link("b", "a")

env.delete("a")
env.delete("b")

env.print_rc()
```

Result:
```
a deleted!
b deleted!
Nothing!
```
##### Chain of three references
```
env = Env()

env.new("a")
env.new("b")
env.new("c")

env.link("a", "b")
env.link("b", "c")

env.delete("a")
env.delete("b")
env.delete("c")

env.print_rc()
```
Result:
```
a deleted!
b deleted!
c deleted!
Nothing!
```
##### Self-reference
```
env = Env()

env.new("a")

env.link("a", "a")

env.delete("a")

env.print_rc()
```

Result:
```
a deleted!
Nothing!
```
All give zero refcounts at the end, with no leaks or errors.
### Conclusion
Sometimes progress isn’t about inventing something new, but about finishing what was once left incomplete.
Reference counting does not need additional GC if we consider the entire world of objects-including the scope-as a single graph of ownership.
Symmetric RC is simple, deterministic, and does not require traversal.
And perhaps it is this simplicity that classic memory management systems have always lacked.
> P.S.
The code is a prototype, but the principle can be transferred to any language: C, Rust, Swift, or even a real VM interpreter.
The main thing is to follow the rule of symmetry: whoever creates a reference is responsible for removing it.