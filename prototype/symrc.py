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

	def delete_link(self):
		if self.ref:
			self.ref.rc_dec()
			self.ref = None

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

	def delete_link(self, name):
		self.objects[name].delete_link()

	def print_rc(self):
		if len(self.objects) != 0:
			for obj in self.objects.values():
				print(f"RC {obj.name}: {obj.refcount}")
		else:
			print("Nothing!")

# env = Env()

# env.new("a")
# env.new("b")

# env.link("a", "b")
# env.link("b", "a")

# a = env.get("a")
# b = env.get("b")

# env.delete("a")
# env.delete("b")

# env.print_rc() # Ничего не выведет, в "области видимости" ничего нет

# print("RC a:", a.refcount) # 0
# print("RC b:", b.refcount) # 0

# print("\n---next---\n")

# env = Env()

# env.new("x")
# env.new("y")

# env.link("x", "y")

# env.print_rc()  # RC x: 1, RC y: 2

# env.delete("x")

# env.print_rc()  # RC y: 1 (остаётся только в области видимости)

# env.delete("y")

# env.print_rc()  # ничего не выводит

# print("RC x:", env.objects.get("x", "удалён"))
# print("RC y:", env.objects.get("y", "удалён"))

# print("\n---next---\n")

# env = Env()

# env.new("a")
# env.new("b")
# env.new("c")

# env.link("a", "b")
# env.link("b", "c")

# env.print_rc()  # RC a: 1, RC b: 2, RC c: 2

# env.delete("a")  # a -> b rc_dec()

# env.print_rc()  # RC b: 1, RC c: 2

# env.delete("b")  # b -> c rc_dec()

# env.print_rc()  # RC c: 1

# env.delete("c")

# env.print_rc()  # пусто

# print("\n---next---\n")

# env = Env()

# env.new("a")
# env.new("b")

# env.link("a", "b")
# env.link("b", "a")

# # env.get("a").ref = None  # вручную разорвали цикл

# env.print_rc()

# env.delete("a")

# env.print_rc() # он бы вывел еще a, но мы смотрим с точки зрения Env, а из окружения к нему не попасть

# env.delete("b")

# env.print_rc()  # пусто


# env = Env()

# env.new("a")
# env.new("b")

# env.link("a", "b")
# env.link("b", "a")

# env.print_rc()  # RC a: 2, RC b: 2

# a = env.get("a")
# b = env.get("b")

# env.delete_link("a")

# env.delete("a")
# env.delete("b")

# env.print_rc()  # пусто

# # print("RC a:", a.refcount)
# # print("RC b:", b.refcount)


# env = Env()

# # # первый цикл
# # env.new("a1"); env.new("b1")
# # env.link("a1", "b1")
# # env.link("b1", "a1")

# # # второй цикл
# # env.new("a2"); env.new("b2"); env.new("c2")
# # env.link("a2", "b2")
# # env.link("b2", "c2")
# # env.link("c2", "a2")

# # env.print_rc()

# # # удаляем всё
# # for name in ["a1","b1","a2","b2","c2"]:
# #     env.delete(name)

# # env.print_rc()

# # env.new("a")

# # env.link("a", "a")

# # env.delete("a")

# # env.print_rc()
