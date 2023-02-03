# Class used to store information for a wire
# From Prof code
class Node(object):

  def __init__(self, name, value, gatetype, innames):
    self.name = name
    self.value = value
    self.gatetype = gatetype
    self.interms = []
    self.innames = innames
    self.is_input = False
    self.is_output = False
    self.is_fault = False

  def set_value(self, v):
    self.value = v

  def display(self):
    if self.is_input:
      nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}"
      print(nodeinfo)
      return
    elif self.is_output:
      nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
    else:  # internal nodes
      nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"

    interm_str = " "
    interm_val_str = " "
    for i in self.interms:
      interm_str += str(i.name) + " "
      interm_val_str += str(i.value) + " "

    nodeinfo += f"as {self.gatetype:>5}"
    nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"
    print(nodeinfo)
    return

  # calculates the value of a node based on its gate type and values at interms
  def calculate_value(self):

    for i in self.interms:
      if i.value != "0" and i.value != "1":
        return "U"

    if self.gatetype == "AND":
      val = "1"
      for i in self.interms:
        if i.value == "0":
          val = "0"
      self.value = val
      return val
    elif self.gatetype == "OR":
      val = "0"
      for i in self.interms:
        if i.value == '1':
          val = "1"
      self.value = val
      return val
    elif self.gatetype == "NAND":
      flag = "1"
      for i in self.interms:
        if i.value == "0":
          flag = "0"
      val = str(1 - int(flag))
      self.value = val
      return val
    elif self.gatetype == "NOT":
      val = self.interms[0].value
      self.value = str(1 - int(val))
      return val
    elif self.gatetype == "XOR":
      num_of_1 = 0
      for i in self.interms:
        if i.value == "1":
          num_of_1 = num_of_1 + 1
      val = num_of_1 % 2
      val = str(val)
      self.value = val
      return val
    elif self.gatetype == "XNOR":
      num_of_1 = 0
      for i in self.interms:
        if i.value == "1":
          num_of_1 = num_of_1 + 1
      val = num_of_1 % 2
      self.value = str(1 - val)
      return val
    elif self.gatetype == "NOR":
      flag = "0"
      for i in self.interms:
        if i.value == "1":
          flag = "1"
      val = str(1 - int(flag))
      self.value = val
      return val
    elif self.gatetype == "BUFF":
      val = self.interms[0].value
      self.value = val
      return val


# from prof code
def parse_gate(rawline):
  # get rid of all spaces
  line = rawline.replace(" ", "")
  # now line = a'=NAND(b',256,c')

  name_end_idx = line.find("=")
  node_name = line[0:name_end_idx]
  # now node_name = a'

  gt_start_idx = line.find("=") + 1
  gt_end_idx = line.find("(")
  node_gatetype = line[gt_start_idx:gt_end_idx]
  # now node_gatetype = NAND

  # get the string of interms between ( ) to build tp_list
  interm_start_idx = line.find("(") + 1
  end_position = line.find(")")
  temp_str = line[interm_start_idx:end_position]
  tp_list = temp_str.split(",")
  # now tp_list = [b', 256, c]

  node_innames = [i for i in tp_list]
  # now node_innames = [b', 256, c]

  return node_name, node_gatetype, node_innames


# from prof code
def construct_nodelist(node_list):
  o_name_list = []

  for line in input_file_values:
    if line == "\n":
      continue
    if line.startswith("#"):
      continue
    if line.startswith("INPUT"):
      index = line.find(")")
      # intValue = str(line[6:index])
      name = str(line[6:index])
      n = Node(name, "U", "PI", [])
      n.is_input = True
      node_list.append(n)
    elif line.startswith("OUTPUT"):
      index = line.find(")")
      name = line[7:index]
      o_name_list.append(name)
    else:  # majority of internal gates processed here
      node_name, node_gatetype, node_innames = parse_gate(line)
      n = Node(node_name, "U", node_gatetype, node_innames)
      node_list.append(n)

  for n in node_list:
    if n.name in o_name_list:
      n.is_output = True

  # link the interm nodes from parsing the list of node names (string)
  # example: a = AND (b, c, d)
  # thus a.innames = [b, c, d]
  # node = a, want to search the entire node_list for b, c, d
  for node in node_list:
    for cur_name in node.innames:
      for target_node in node_list:
        if target_node.name == cur_name:
          node.interms.append(target_node)

  return


# function for printing output values:-
def printResults(circuit):
  print("input: \t", end="")
  print(*circuit.input_list, end="")
  print("\t = \t", end="")
  print(*circuit.input_val)
  print("output:\t", end="")
  print(*circuit.output_list, end="")
  print("\t = \t", end="")
  print(*circuit.output_val)


# make a circuit class, containing a nodelist, display function, and simulation method:-
class circuit:

  def __init__(self, node_list, fault, val, fname):
    self.node_list = node_list
    self.is_fault = fault
    self.fVal = val
    self.fName = fname
    self.input_list = []
    self.output_list = []
    self.output_val = []
    self.inputVal = []
    self.old_n = ''

  def cir_sim(self):
    updated_count = 1
    iteration = 0
    while updated_count > 0:
      updated_count = 0
      iteration += 1
      for n in node_list:
        if self.is_fault:
          if n.name == self.fName[0]:
            if len(self.fName) > 2:
              for i in n.interms:
                new_node = Node(self.fName[1] + '-f', self.fVal, 'copy', '')
                if i.name == self.fName[1]:
                  self.old_n = i
                  n.interms.remove(i)
                  n.interms.append(new_node)
            else:
              n.is_fault = True
              n.value == self.fVal
              n.set_value(self.fVal)
        if n.value == "U":
          n.calculate_value()
          if n.value == "0" or n.value == "1":
            updated_count += 1
    self.input_list = [i.name for i in self.node_list if i.is_input]
    self.input_val = [i.value for i in self.node_list if i.is_input]

    self.output_list = [i.name for i in self.node_list if i.is_output]
    self.output_val = [i.value for i in self.node_list if i.is_output]

    # reattaches the correct interm before proceeding
    if self.is_fault:
      for n in node_list:
        if n.name == self.fName[0]:
          if len(self.fName) > 2:
            for i in n.interms:
              if i.name == self.fName[1] + '-f':
                n.interms.remove(i)
                n.interms.append(self.old_n)

    return


# reset function for node_list
def reset(node_list, line_of_val):
  for n in node_list:
    n.set_value("U")
  strindex = 0
  # Set value of input node
  for node in node_list:
    if node.is_input:
      if strindex > len(line_of_val) - 1:
        break
      node.set_value(line_of_val[strindex])
      strindex = strindex + 1


# function for simulation
def sim(fault, faultV, faultName):
  reset(node_list, line_of_val)
  if not fault:
    # print("\n--- Good Simulation results: ---")
    g_circuit = circuit(node_list, False, faultV, faultName)
    g_circuit.cir_sim()
    return g_circuit.output_val
  else:
    print(f'--- Faulty Simulation Results: ---')
    f_circuit = circuit(node_list, True, faultV, faultName)
    f_circuit.cir_sim()
    return f_circuit.output_val


# Main function starts here


class lfsr(object):

  def __init__(self, h_vals, q_vals, type):
    self.h_vals = h_vals
    self.seed_q_vals = q_vals
    self.type = type
    self.tvs = []

  def gen_tvs(self):
    if self.type == 1:
      self.tvs.append(self.seed_q_vals)
      cur = self.seed_q_vals

      while True:
        q_vals = []
        q_vals.append(cur[-1])
        for i in range(1, len(self.h_vals)):
          q_vals.append('U')

        for i in range(1, len(self.h_vals)):
          if self.h_vals[i] == '1':
            q_vals[i] = str(int(cur[i - 1]) ^ int(cur[-1]))
          else:
            q_vals[i] = str(cur[i - 1])
        self.tvs.append(q_vals)
        cur = q_vals
        # print(q_vals)
        if self.tvs[-1] == self.tvs[0]:
          break

        if len(self.tvs) >= 100:
          print('Too many TV'
                's, exited at 100')
          break

    else:
      self.tvs.append(self.seed_q_vals)
      cur = self.seed_q_vals

      while True:
        q_vals = []
        to_be_xored = []
        for i in range(0, len(self.h_vals)):
          q_vals.append('U')

        for i in range(0, len(self.h_vals)):
          q_vals[i] = str(cur[i - 1])
          if self.h_vals[i] == '1':
            to_be_xored.append(cur[i])
        num = to_be_xored.count('1')
        if num % 2 == 0:
          q_vals[0] = '0'
        else:
          q_vals[0] = '1'
        self.tvs.append(q_vals)
        cur = q_vals

        if len(self.tvs) >= 100:
          print('Too many TV'
                's, exited at 100')
          break

        if self.tvs[-1] == self.tvs[0]:
          break


class misr(object):

  def __init__(self, r_list, h_vals, seed):
    self.r_list = r_list
    self.h_vals = h_vals
    self.seed = seed
    self.sig = []

  def find_sig(self):
    cur = []
    cur = self.seed
    # for the length of the responses
    for j in range(len(self.r_list)):
      count = 0
      while True:
        q_vals = []
        # appending q_0
        q_vals.append(str(int(cur[-1]) ^ int(self.r_list[j][0])))

        # just initializing q_n's
        for i in range(1, len(self.h_vals)):
          q_vals.append('U')

        for i in range(1, len(self.h_vals)):
          if self.h_vals[i] == '1':
            q_vals[i] = str(
              int(cur[i - 1]) ^ int(cur[-1]) ^ int(self.r_list[j][i]))
          else:
            q_vals[i] = str(int(cur[i - 1]) ^ int(self.r_list[j][i]))
        count += 1
        if count > len(self.r_list):
          break
      cur = q_vals
    self.sig = cur


# Step 1: get circuit file name from command line
def getFileName():
  wantToInputCircuitFile = str(
    input(
      "Provide a benchfile name (return to accept circuit.bench by default):\n"
    ))

  if len(wantToInputCircuitFile) != 0:
    circuitFile = wantToInputCircuitFile
    try:
      f = open(circuitFile)
      f.close()
    except FileNotFoundError:
      print('File does not exist, setting circuit file to default')
      circuitFile = "circuit.bench"
  else:
    circuitFile = "circuit.bench"
  return circuitFile


# contructing node_list
node_list = []
line_of_val = ''


# for compound fault name parsing
def parsefault(s):
  fault = []
  a = s.split('-')
  fault = a
  return fault


# function to make fault list
def make_fault_list(f_list):
  for n in node_list:
    f_list.append([n.name, "0"])
    f_list.append([n.name, "1"])
    if n.is_output == True:
      f_list.append(["output", n.name, "0"])
      f_list.append(["output", n.name, "1"])
    for i in n.interms:
      f_list.append([n.name, i.name, "0"])
      f_list.append([n.name, i.name, "1"])


while True:
  # getting the filename / opening file
  filename = getFileName()
  file1 = open(filename, "r")
  input_file_values = file1.readlines()
  file1.close()

  # contructing node_list_b
  node_list.clear()
  construct_nodelist(node_list)

  # making fault list
  f_list = []
  make_fault_list(f_list)
  for f in f_list:
    print(f)

  # finding number of inputs
  inCount = 0
  for n in node_list:
    if n.is_input:
      inCount += 1

  print('\n----- Testing All Faults -----')
  seed = input(f'input seed with length = {inCount}\n')
  h_val = input(f'input h values with length = {inCount - 1}\n')

  l_seed = list(seed)
  h_v = list(h_val)
  h_v.insert(0, '1')
  print(l_seed)
  print(h_v)

  some_lfsr = lfsr(h_v, l_seed, 1)
  some_lfsr.gen_tvs()
  print(some_lfsr.tvs)
  r_dict = {}
  g = open('log.txt', 'w')

  for f in f_list:
    out = []
    F = '-'.join(f)
    for tv in some_lfsr.tvs:
      line_of_val = ''.join(tv)
      g.write(line_of_val)
      g.write('\n')
      reset(node_list, line_of_val)
      print(f'Simulating circuit with fault at {f}')
      output = sim(True, f[-1], f)
      out.append(output)
      print(output)
    r_dict[F] = out

  # print(len(r_dict))
  # print(len(f_list))

  good_list = []
  for tv in some_lfsr.tvs:
    line_of_val = ''.join(tv)
    reset(node_list, line_of_val)
    g_output = sim(False, '', '')
    good_list.append(g_output)

  misr_h = input(f'Enter MISR h-values (length of {len(good_list[0]) - 1}):\n')
  misr_s = input(f'Enter MISR seed (length of {len(good_list[0])}):\n')
  m_seed = list(misr_s)
  h_v_m = list(misr_h)
  h_v_m.insert(0, '1')
  print(h_v_m)

  g_sig = misr(good_list, h_v_m, m_seed)
  g_sig.find_sig()
  d_count = 0
  print(f'\nThis is the good sig: {g_sig.sig}')
  print()

  for r in r_dict:
    f_sig = misr(r_dict[r], h_v_m, m_seed)
    f_sig.find_sig()
    print(f'sig for fault {r} = {f_sig.sig}', end="")
    b = False
    for i in range(len(g_sig.sig)):
      if g_sig.sig[i] != f_sig.sig[i]:
        b = False
        break
      else:
        b = True
    if b:
      print(' = NOT DETECTED')
    else:
      d_count += 1
      print(' = DETECTED')
  print(f'\nNumber of faults detected out of {len(r_dict)}: {d_count}\n')
# end