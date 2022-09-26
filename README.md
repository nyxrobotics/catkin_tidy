### catkin_tidy

Run clang-tidy with catkin command

### usage

- Build with clang

```
catkin clang_build <package_name>
```

- Format with clang-tidy
  - Source files will be overwritten, so be sure to make a backup before executing
  - If the naming modification is complex, it may not be possible to fully modify the naming. In such cases, please manually modify them by looking at the diffs

```
catkin clang_tidy <package_name>
```

### install

```
mkdir -p ~/lib
cd ~/lib
git clone https://github.com/nyxrobotics/catkin_tidy.git
cd catkin_tidy
pip install .
```

### uninstall

```
pip uninstall catkin-tidy -y
```
