class Cut:
    def __init__(self, name, parent=None, left=None, right=None, 
                 n_pass=0, n_pass_weighted=0., n_fail=0, n_fail_weighted=0.):
        self.name = name
        self.n_pass = n_pass
        self.n_pass_weighted = n_pass_weighted
        self.n_fail = n_fail
        self.n_fail_weighted = n_fail_weighted
        self.parent = parent
        self.left = left
        self.right = right

    def __eq__(self, other_cut):
        if self.parent:
            same_parent = (self.parent.name == other_cut.parent.name)
        else:
            same_parent = (not self.parent and not other_cut.parent)
        if self.left:
            same_left = (self.left.name == other_cut.left.name)
        else:
            same_left = (not self.left and not other_cut.left)
        if self.right:
            same_right = (self.right.name == other_cut.right.name)
        else:
            same_right = (not self.right and not other_cut.right)
        same_lineage = (same_parent and same_left and same_right)
        same_name = (self.name == other_cut.name)
        return same_name and same_lineage

    def __add__(self, other_cut):
        if self == other_cut:
            cut_sum = Cut(
                self.name,
                n_pass=(self.n_pass + other_cut.n_pass),
                n_pass_weighted=(self.n_pass_weighted + other_cut.n_pass_weighted),
                n_fail=(self.n_fail + other_cut.n_fail),
                n_fail_weighted=(self.n_fail_weighted + other_cut.n_fail_weighted),
            )
            return cut_sum
        else:
            raise ValueError("can only add equivalent cuts")

    def __sub__(self, other_cut):
        if self == other_cut:
            cut_diff = Cut(
                self.name,
                n_pass=(self.n_pass - other_cut.n_pass),
                n_pass_weighted=(self.n_pass_weighted - other_cut.n_pass_weighted),
                n_fail=(self.n_fail - other_cut.n_fail),
                n_fail_weighted=(self.n_fail_weighted - other_cut.n_fail_weighted),
            )
            return cut_diff
        else:
            raise ValueError("can only add equivalent cuts")

    def ancestry(self):
        next_parent = self.parent
        while next_parent:
            yield next_parent
            next_parent = next_parent.parent

    def efficiency(self):
        return self.n_pass_weighted/(self.n_pass_weighted + self.n_fail_weighted)

class Cutflow:
    def __init__(self):
        self.__cuts = {}
        self.__root_cut_name = None
        self.__terminal_cut_names = []

    def __len__(self):
        return len(self.__cuts)

    def __getitem__(self, name):
        return self.__cuts[name]

    def __eq__(self, other_cutflow):
        return self.get_cut_network() == other_cutflow.get_cut_network()

    def __add__(self, other_cutflow):
        if len(self) == 0:
            return other_cutflow
        elif len(other_cutflow) == 0:
            return self
        elif self != other_cutflow:
            raise ValueError("can only add equivalent cutflows")
        else:
            summed_cuts = {}
            for name, cut in self.items():
                other_cut = other_cutflow[name]
                summed_cuts[name] = cut + other_cut
            return Cutflow.from_network(summed_cuts, self.get_cut_network())

    def __sub__(self, other_cutflow):
        if len(self) == 0:
            return other_cutflow
        elif len(other_cutflow) == 0:
            return self
        elif self != other_cutflow:
            raise ValueError("can only add equivalent cutflows")
        else:
            diffed_cuts = {}
            for name, cut in self.items():
                other_cut = other_cutflow[name]
                diffed_cuts[name] = cut - other_cut
            return Cutflow.from_network(diffed_cuts, self.get_cut_network())

    def __recursive_find_terminals(self, cut_name):
        cut = self.__cuts[cut_name]
        if not cut.right and not cut.left:
            self.__terminal_cut_names.append(cut_name)
        else:
            if cut.right:
                self.__recursive_find_terminals(cut.right.name)
            if cut.left:
                self.__recursive_find_terminals(cut.left.name)

    def __recursive_print(self, cut, tabs=""):
        if cut is self.root_cut():
            prefix = ""
        elif cut is cut.parent.left:
            if not cut.parent.right:
                prefix = f"{tabs}\u2514\u2612\u2500"
                tabs += "    "
            else:
                prefix = f"{tabs}\u251C\u2612\u2500"
                tabs += "\u2502   "
        elif cut is cut.parent.right:
            prefix = f"{tabs}\u2514\u2611\u2500"
            tabs += "    "

        print(f"{prefix}{cut.name}")
        if not cut.right or cut.n_pass != cut.right.n_pass:
            print(f"{tabs}pass: {cut.n_pass} (raw) {cut.n_pass_weighted:0.2f} (wgt)")
            print(f"{tabs}fail: {cut.n_fail} (raw) {cut.n_fail_weighted:0.2f} (wgt)")

        if cut.left:
            self.__recursive_print(cut.left, tabs=tabs)
        if cut.right:
            self.__recursive_print(cut.right, tabs=tabs)
    
    @property
    def terminal_cut_names(self):
        self.__recursive_find_terminals(self.__root_cut_name)
        return self.__terminal_cut_names

    def print(self):
        self.__recursive_print(self.root_cut())

    def items(self):
        return self.__cuts.items()

    def cut_names(self):
        return self.__cuts.keys()

    def cuts(self):
        return self.__cuts.values()

    def set_root_cut(self, new_cut):
        self.__root_cut_name = new_cut.name
        self.__cuts[new_cut.name] = new_cut

    def root_cut(self):
        return self.__cuts[self.__root_cut_name]

    def insert(self, target_cut_name, new_cut, direction="right"):
        if new_cut.name in self.__cuts:
            raise ValueError(f"{new_cut.name} already exists in this cutflow")

        target_cut = self.__getitem__(target_cut_name)
        new_cut.parent = target_cut

        if direction.lower() == "right":
            if target_cut.right:
                new_cut.right = target_cut.right
                target_cut.right.parent = new_cut
            target_cut.right = new_cut
        elif direction.lower() == "left":
            if target_cut.right:
                new_cut.left = target_cut.left
                target_cut.left.parent = new_cut
            target_cut.left = new_cut
        else:
            raise ValueError(f"direction can only be 'right' or 'left' not '{direction}'")
        self.__cuts[new_cut.name] = new_cut

    def get_cut_network(self):
        cut_network = {}
        for cut in self.__cuts.values():
            parent = cut.parent.name if cut.parent else None
            left = cut.left.name if cut.left else None
            right = cut.right.name if cut.right else None
            cut_network[cut.name] = (parent, left, right)
        return cut_network

    def get_mermaid(self, cut, content=""):
        if cut is self.root_cut():
            content += f"    {cut.name}([\"{cut.name} <br/> (root node)\"])\n"
        else:
            if cut is cut.parent.left:
                content += f"    {cut.parent.name}Fail --> {cut.name}{{{cut.name}}}\n"
            elif cut is cut.parent.right:
                content += f"    {cut.parent.name}Pass --> {cut.name}{{{cut.name}}}\n"
        fail_node = f"[/{cut.n_fail} raw <br/> {cut.n_fail_weighted:0.2f} wgt/]"
        content += f"    {cut.name} -- Fail --> {cut.name}Fail{fail_node}\n"
        pass_node = f"[/{cut.n_pass} raw <br/> {cut.n_pass_weighted:0.2f} wgt/]"
        content += f"    {cut.name} -- Pass --> {cut.name}Pass{pass_node}\n"
        if cut.left:
            content = self.get_mermaid(cut.left, content=content)
        if cut.right:
            content = self.get_mermaid(cut.right, content=content)
        return content

    def get_csv(self, terminal_cut):
        content = "cut,raw,wgt\n"
        cuts = list(terminal_cut.ancestry()) # ordered parent -> root
        cuts.reverse() # ordered root -> parent
        cuts.append(terminal_cut)
        for cut_i, cut in enumerate(cuts):
            if cut is terminal_cut:
                write_passes = True
            elif cut is terminal_cut.parent:
                write_passes = (cut.right is terminal_cut)
            else:
                write_passes = (cut.right is cuts[cut_i+1])
            if write_passes:
                content += f"{cut.name},{cut.n_pass},{cut.n_pass_weighted:0.2f}"
            else:
                content += f"not({cut.name}),{cut.n_fail},{cut.n_fail_weighted:0.2f}"
            if cut_i < len(cuts) - 1:
                content += "\n"

        return content

    def write_mermaid(self, output_mmd, orientation="TD"):
        with open(output_mmd, "w") as f_out:
            f_out.write(f"```mermaid\ngraph {orientation}\n")
            f_out.write(self.get_mermaid(self.root_cut()))
            f_out.write("```")

    def write_csv(self, output_csv, terminal_cut_name):
        terminal_cut = self.__cuts[terminal_cut_name]
        with open(output_csv, "w") as f_out:
            f_out.write(self.get_csv(terminal_cut))
            f_out.write("\n")

    @staticmethod
    def from_network(cuts, cut_network):
        cutflow = Cutflow()
        # Check inputs
        if not set(cuts) == set(cut_network.keys()):
            raise ValueError("list of cuts does not match cut network")
        # Build cutflow
        cutflow.__cuts = cuts
        cutflow.__cut_network = cut_network
        for name, (parent_name, left_name, right_name) in cut_network.items():
            if parent_name:
                cutflow.__cuts[name].parent = cutflow.__cuts[parent_name]
            else:
                if cutflow.__root_cut_name:
                    raise Exception("invalid cutflow - multiple root cuts")
                else:
                    cutflow.__root_cut_name = name
            if left_name:
                cutflow.__cuts[name].left = cutflow.__cuts[left_name]
            if right_name:
                cutflow.__cuts[name].right = cutflow.__cuts[right_name]
        # Check cutflow and return it if it is healthy
        if not cutflow.__root_cut_name:
            raise Exception("invalid cutflow - no root cut")
        else:
            return cutflow

    @staticmethod
    def from_text(cflow_text, delimiter=","):
        cuts = {}
        cut_network = {}
        for line in cflow_text.split("\n"):
            # Read cut attributes
            cut_attr = line.split(delimiter)
            # Extract basic info
            name = cut_attr[0]
            n_pass, n_pass_weighted, n_fail, n_fail_weighted = cut_attr[1:5]
            # Cast string counts into numbers
            n_pass = int(n_pass)
            n_fail = int(n_fail)
            n_pass_weighted = float(n_pass_weighted)
            n_fail_weighted = float(n_fail_weighted)
            # Extract lineage
            parent_name, left_name, right_name = cut_attr[5:]
            # Cast 'null' values into NoneType
            if parent_name == "null":
                parent_name = None
            if left_name == "null":
                left_name = None
            if right_name == "null":
                right_name = None
            # Create new cut and update cut network
            cuts[name] = Cut(
                name, 
                n_pass=n_pass, n_pass_weighted=n_pass_weighted, 
                n_fail=n_fail, n_fail_weighted=n_fail_weighted
            )
            cut_network[name] = (parent_name, left_name, right_name)

        return Cutflow.from_network(cuts, cut_network)

    @staticmethod
    def from_file(cflow_file, delimiter=","):
        with open(cflow_file, "r") as f_in:
            cflow_text = f_in.read()

        return Cutflow.from_text(cflow_text, delimiter=delimiter)

class CutflowCollection:
    def __init__(self, cutflows={}):
        self.__cutflows = {}
        if cutflows:
            if type(cutflows) == dict:
                self.__cutflows = cutflows
            elif type(cutflow_objs) == list:
                for cutflow_i, cutflow in enumerate(cutflows):
                    self.__cutflows[f"Cutflow_{cutflow_i}"] = cutflow
            else:
                raise ValueError("cutflows must be arranged in a dict or list")
        self.__consistency_check()

    def __getitem__(self, name):
        return self.__cutflows[name]

    def __setitem__(self, name, cutflow):
        self.__consistency_check(new_cutflow=cutflow)
        self.__cutflows[name] = cutflow
    
    def __contains__(self, name):
        return name in self.__cutflows.keys()

    def __add__(self, other_collection):
        summed_collection = {}
        names = set(self.names)
        other_names = set(other_collection.names)
        # Add cutflows with the same name
        for name in (names & other_names):
            summed_collection[name] = self.__cutflows[name] + other_collection[name]
        # Collect the rest
        for name in (names - other_names):
            summed_collection[name] = self.__cutflows[name]
        for name in (other_names - names):
            summed_collection[name] = other_collection[name]
        return CutflowCollection(summed_collection)

    def __consistency_check(self, new_cutflow=None):
        # Check cutflow equivalence
        if len(self.cutflows) == 0:
            return
        elif new_cutflow:
            if new_cutflow != self.cutflows[-1]:
                raise Exception("new cutflow is inconsistent with cutflows in collection")
        else:
            for cutflow_i, cutflow in enumerate(self.cutflows[:-1]):
                if cutflow != self.cutflows[cutflow_i+1]:
                    raise Exception("cutflows are inconsistent")
    
    @property
    def terminal_cut_names(self):
        if self.cutflows:
            return self.cutflows[0].terminal_cut_names
        else:
            return []

    @property
    def names(self):
        return list(self.__cutflows.keys())

    @property
    def cutflows(self):
        return list(self.__cutflows.values())

    def items(self):
        return self.__cutflows.items()

    def pop(self, name):
        return self.__cutflows.pop(name)

    def sum(self):
        cutflow_sum = Cutflow()
        for cutflow in self.cutflows:
            cutflow_sum += cutflow
        return cutflow_sum

    def reorder(self, ordered_names):
        mismatches = set(self.names) - set(ordered_names)
        if len(mismatches) > 0:
            raise ValueError(
                f"given cutflow names do not match current set; mismatches:\n{mismatches}"
            )
        self.__cutflows = {n: self.__cutflows[n] for n in ordered_names}

    def rename(self, rename_map):
        old_names = self.names
        new_names = [n if n not in rename_map else rename_map[n] for n in old_names]
        self.__cutflows = {
            new_n: self.__cutflows[old_n] for old_n, new_n in zip(old_names, new_names)
        }

    def get_csv(self, terminal_cut_name):
        rows = []
        for cutflow_i, (cutflow_name, cutflow) in enumerate(self.items()):
            terminal_cut = cutflow[terminal_cut_name]
            cutflow_rows = cutflow.get_csv(terminal_cut).split("\n")
            if cutflow_i == 0:
                header = ["," for col in cutflow_rows[0].split(",")[:-1]]
                header.insert(1, cutflow_name)
                header = "".join(header)
                cutflow_rows.insert(0, header)
                rows = cutflow_rows
            else:
                # Trim cut name column
                cutflow_rows = [",".join(r.split(",")[1:]) for r in cutflow_rows]
                # Concatenate with existing rows
                header = ["," for col in cutflow_rows[0].split(",")[:-1]]
                header.insert(0, cutflow_name)
                header = "".join(header)
                cutflow_rows.insert(0, header)
                for row_i, cutflow_row in enumerate(cutflow_rows):
                    rows[row_i] = f"{rows[row_i]},{cutflow_row}"
        return rows

    def write_csv(self, output_csv, terminal_cut_name):
        with open(output_csv, "w") as f_out:
            f_out.write("\n".join(self.get_csv(terminal_cut_name)))
            f_out.write("\n")

    @staticmethod
    def from_files(cflow_files, delimiter=","):
        if type(cflow_files) == list:
            cutflows = []
            for cflow_file in cflow_files:
                cutflows.append(Cutflow.from_file(cflow_file, delimiter=delimiter))
            return CutflowCollection(cutflows)
        elif type(cflow_files) == dict:
            cutflows = {}
            for cutflow_name, cflow_file in cflow_files:
                cutflows[cutflow_name] = Cutflow.from_file(cflow_file, delimiter=delimiter)
            return CutflowCollection(cutflows)
        else:
            raise ValueError("cutflow files must be arranged in a dict or list")
