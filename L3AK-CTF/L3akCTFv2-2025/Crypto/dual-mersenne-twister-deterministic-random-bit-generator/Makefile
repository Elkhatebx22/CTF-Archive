CC = gcc
CFLAGS = -fPIC -O2 -Wall -shared
SRC = f2_solve.c
PYTHON_INC := $(shell python3 -c "from sysconfig import get_paths as gp; print(gp()['include'])")
NUMPY_INC := $(shell python3 -c "import numpy; print(numpy.get_include())")
LDFLAGS = -lm4ri
INCLUDES = -I$(PYTHON_INC) -I$(NUMPY_INC)
TARGET = f2_solve$(shell python3-config --extension-suffix)

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(INCLUDES) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)