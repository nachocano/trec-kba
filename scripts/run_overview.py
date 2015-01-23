#!/usr/bin/python
import argparse
import matplotlib.pyplot as plt

alphas = [0.2,0.4,0.6,0.8]
gds = [0.2,0.5,1,20,30,50,70,100]
gis = [0.1,0.5,0.9]

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-o', '--overview_file', required=True)
  args = parser.parse_args()

  runs = {}
  with open(args.overview_file) as f:
    for line in f.read().splitlines():
      if line.startswith("#"):
        continue
      line = line.split(",")
      print '%s\t %.3f & %.3f & %.3f & %.3f & %.3f & %.3f &' % (line[1], float(line[2]), float(line[3]), float(line[4]), float(line[6]), float(line[7]), float(line[8]))
      runs[line[1]] = (float(line[6]), float(line[7]), float(line[8]))

  exit()
  keys = []
  for key in runs:
    if "gd1_gi01" in key:
      keys.append(key)
  keys.sort()
  plot_alpha(runs, keys)
  exit()

  keys = []
  for key in runs:
    if "a08" in key:
      keys.append(key)
  keys.sort()

  gds = []
  for key in keys:
    if "gi01" in key:
      gds.append(key)
  aux = gds[2]
  gds[2] = gds[3]
  gds[3] = gds[4]
  gds[4] = gds[5]
  gds[5] = gds[6]
  gds[6] = gds[7]
  gds[7] = aux
  print gds

  plot_gds(runs, gds)

  gis = []
  for key in keys:
    if "gd1_" in key:
      gis.append(key)
  gis.sort()
  print gis
  plot_gis(runs, gis)

def plot_gds(runs, keys):
  precisions = []
  recalls = []
  f1s = []

  for key in keys:
    p, r, f1 = runs[key]
    precisions.append(p)
    recalls.append(r)
    f1s.append(f1)

  fig = plt.figure()
  fig.suptitle("P-R-F1 alpha = 0.8 gamma_inc = 0.1", fontsize=13, fontweight='bold')
  sc1 = plt.scatter(gds, recalls, color='b', label='recall')
  sc2 = plt.scatter(gds, precisions, color='y', label='precision')
  sc3 = plt.scatter(gds, f1s, color='g', label='f1')
  plt.legend(loc=1)
  plt.xlabel("gamma_dec")
  plt.show()

def plot_gis(runs, keys):
  precisions = []
  recalls = []
  f1s = []

  for key in keys:
    p, r, f1 = runs[key]
    precisions.append(p)
    recalls.append(r)
    f1s.append(f1)

  fig = plt.figure()
  fig.suptitle("P-R-F1 alpha = 0.8 gamma_dec = 1", fontsize=13, fontweight='bold')
  sc1 = plt.scatter(gis, recalls, color='b', label='recall')
  sc2 = plt.scatter(gis, precisions, color='y', label='precision')
  sc3 = plt.scatter(gis, f1s, color='g', label='f1')
  plt.legend(loc='upper left')
  plt.xlabel("gamma_inc")
  plt.show()

def plot_alpha(runs, keys):
  precisions = []
  recalls = []
  f1s = []

  for key in keys:
    p, r, f1 = runs[key]
    precisions.append(p)
    recalls.append(r)
    f1s.append(f1)

  fig = plt.figure()
  #fig.suptitle("P-R-F1 gamma_inc = 0.1 gamma_dec = 1", fontsize=13, fontweight='bold')
  sc1 = plt.plot(alphas, recalls, color='b', label='recall')
  sc2 = plt.plot(alphas, precisions, color='y', label='precision')
  sc3 = plt.plot(alphas, f1s, color='g', label='f1')
  plt.legend(loc="lower left")
  plt.xlabel("alpha")
  plt.show()


if __name__ == '__main__':
  main()