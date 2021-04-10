from .application import Application, ApplicationError
import sys

def main():
	try:
		app = Application(sys.argv)
	except ApplicationError as e:
		sys.exit('cmeson: ' + str(e))

if __name__ == '__main__':
	main()