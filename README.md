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
sudo apt isntall clang-format-13 clang-tidy-13
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

### Reference
- [ipa-fez/tipsntricks](https://github.com/ipa-fez/tipsntricks/blob/master/clang/catkin_tidy/catkin_tidy/tidy.py)
