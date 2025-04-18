from myCSP.myVariable import *
from myCSP.myVarArray import *
from myCSP.myConstraint import *
from myCSP.AllDifferent import *
from board import Board
from refresher import Refresher

from queue import Queue

# my_variables = [] is declared in myVariable.py
constraint_list = []
g: myConstraintGraph

def my_satisfy(*constraints: Union[myConstraint, myAllDifferent]) -> None:
    """
    Adds constraints to the constraint list and initializes the constraint graph.
    
    :param constraints: A variable number of constraint objects (either myConstraint or myAllDifferent).
    """
    for constraint in constraints:
        if isinstance(constraint, myAllDifferent):
            constraint_list.extend(constraint.get_constraints())
        else:
            constraint_list.append(constraint)

    global g
    g = myConstraintGraph(constraint_list)
    

def my_solve(do_unary_check: bool, 
             do_arc_consistency: bool, 
             do_mrv: bool, 
             do_lcv: bool, 
             refresher: Refresher) -> bool:
    """
    Solves the CSP problem using backtracking with optional heuristics.
    
    :param do_unary_check: If True, performs node consistency.
    :param do_arc_consistency: If True, applies arc consistency during backtracking.
    :param do_mrv: If True, applies Minimum Remaining Values (MRV) heuristic.
    :param do_lcv: If True, applies Least Constraining Value (LCV) heuristic.
    :param refresher: A Refresher object to update the UI during solving.
    Use `refresher.refresh_screen()` in middle of your code to update the sudoku on screen.
    :return: True if a solution is found, False otherwise.
    :raises: `StopAlgorithmException` if user clicks on 'Stop' or exit button.
    You do not need to handle this; it's handled in `main.py`.
    """

    # node consistency
    if do_unary_check:
        if not node_consistency(refresher):
            return False

    # backtrack 
    if not backtrack(do_arc_consistency, do_mrv, do_lcv , True, refresher):
        return False

    return True

def my_clear():
    """
    Clears variables and constraints for a fresh CSP instance.
    """
    my_variables = []
    constraint_list = []
    g = None

def node_consistency(refresher: Refresher) -> bool:
    """
    Applies node consistency by filtering values that do not satisfy unary constraints.
8
    Use `g.is_node_satisfied(v, d)` to check if `d` is satisfied for variable `v`
    
    :param refresher: A Refresher object to update the UI.
    :return: True if node consistency is maintained, False otherwise.
    """

    for v in my_variables:
        # Skip variables that already have a value assigned 
        if v.value is not None:
            continue
            
        # Create a list to store values that satisfy the unary constraints
        valid_values = []
        
        # Check each value in the variable's domain
        

        for d in v.remaining_domain:
            if g.is_node_satisfied(v, d):
                valid_values.append(d)
        
        # Update the variable's domain with only valid values
        v.remaining_domain = valid_values
        
        # If any variable's domain becomes empty, the puzzle is unsolvable
        if not v.remaining_domain:
            return False
        
        # Update the GUI to reflect domain changes
        refresher.refresh_screen()

    return True

def backtrack(do_arc_consistency: bool, do_mrv: bool, do_lcv: bool, do_degree: bool, refresher: Refresher) -> bool:  # Added do_degree parameter
    if g.is_assignment_complete():
        return True

    var = select_unassigned_variable(do_mrv, do_degree)  # Pass do_degree to selector
    for value in order_domain_values(var, do_lcv):
        # Temporary assignment
        old_value = var.value
        var.value = value
        var.remaining_domain = [value]
        refresher.refresh_screen()

        # Apply forward checking (or AC-3 if enabled)
        backup_domains = extract_domains()
        if do_arc_consistency:
            consistent = arc_consistency(refresher)  # Use AC-3
        else:
            consistent = forward_checking(var, value, refresher)  # Use forward checking

        if consistent:
            result = backtrack(do_arc_consistency, do_mrv, do_lcv, do_degree, refresher)  # Pass do_degree
            if result:
                return True

        # Backtrack if no solution found
        restore_domains(backup_domains)
        var.value = old_value
        var.remaining_domain = backup_domains[var]
        refresher.refresh_screen()
    return False

def backtrack1(do_arc_consistency: bool, do_mrv: bool, do_lcv: bool, refresher: Refresher) -> bool:
    if g.is_assignment_complete():
        return True

    var = select_unassigned_variable(do_mrv)
    for value in order_domain_values(var, do_lcv):
        # Temporary assignment
        old_value = var.value
        var.value = value
        var.remaining_domain = [value]
        refresher.refresh_screen()

        # Apply forward checking (or AC-3 if enabled)
        backup_domains = extract_domains()
        if do_arc_consistency:
            consistent = arc_consistency(refresher)  # Use AC-3
        else:
            consistent = forward_checking(var, value, refresher)  # Use forward checking

        if consistent:
            result = backtrack(do_arc_consistency, do_mrv, do_lcv, refresher)
            if result:
                return True

        # Backtrack if no solution found
        restore_domains(backup_domains)
        var.value = old_value
        var.remaining_domain = backup_domains[var]
        refresher.refresh_screen()
    return False


def select_static_order_variable() -> myVariable:
    """
    Returns the first unassigned variable in static order (left-to-right, top-to-bottom).
    """
    for v in my_variables:
        if v.value is None:
            return v
    return None

def static_order_domains(v: myVariable) -> List[int]:
    """
    Returns the domain values in their original order.
    """
    return v.remaining_domain


def inference1(do_arc_consistency: bool, refresher: Refresher) -> bool:
    """
    Uses forward-checking methods to eliminate variable domains that cause contradiction in the future. 
    """
    if do_arc_consistency:
        return arc_consistency(refresher)
    
    else:
        # Forward checking requires knowing the last assigned var/value,
        # so we assume they're stored in the graph or refresher.
        # You may need to modify this part based on your actual implementation.
        last_var = g.neighbors()  # Hypothetical method
        last_value = last_var.value if last_var else None
        if last_var and last_value is not None:
            return forward_checking(last_var, last_value, refresher)
        return True

    #return True
def inference(do_arc_consistency: bool, refresher: Refresher, 
             current_var: myVariable = None, current_value: int = None) -> bool:
    """
    Apply either arc consistency or forward checking.
    Now accepts optional current_var and current_value for forward checking.
    """
    if do_arc_consistency:
        return arc_consistency(refresher)
    elif current_var is not None and current_value is not None:
        return forward_checking(current_var, current_value, refresher)
    return True

def forward_checking(var: myVariable, value: int, refresher: Refresher) -> bool:
    """
    Prune neighbor domains after assignment.
    Uses get_neighbors() from the constraint graph.
    """
    for neighbor in g.neighbors(var):  # Using existing get_neighbors()
        if neighbor.value is None:
            neighbor.remaining_domain = [
                d for d in neighbor.remaining_domain 
                if g.is_arc_satisfied(var, neighbor, value, d)
            ]
            refresher.refresh_screen()
            if not neighbor.remaining_domain:
                return False
    return True

def arc_consistency(refresher: Refresher) -> bool:
    """
    Enforces arc consistency using AC-3 algorithm with Queue.
    Returns False if any domain becomes empty (inconsistency), True otherwise.
    """
    queue = g.get_arcs()  # Get the Queue object

    while not queue.empty():  # While queue is not empty
        v1, v2 = queue.get()  # Dequeue an arc (v1, v2)
        if revise(v1, v2):
            if not v1.remaining_domain:
                return False  # Inconsistent domain
            # Add neighboring arcs (vk, v1) where vk != v2
            for vk in g.neighbors(v1):
                if vk != v2:
                    queue.put((vk, v1))
            refresher.refresh_screen()  # Optional GUI update
    return True  # All domains consistent



def revise(v1: myVariable, v2: myVariable) -> bool:
    """
    Revises the domain of v1 by removing values that conflict with v2.
    Returns True if the domain was revised, False otherwise.
    """
    revised = False
    for x in list(v1.remaining_domain):  # Iterate over a copy of the domain
        # Check if there exists any y in v2's domain that satisfies the constraint
        has_support = any(
            g.is_arc_satisfied(v1, v2, x, y)
            for y in v2.remaining_domain
        )
        if not has_support:
            v1.remaining_domain.remove(x)  # Remove invalid value
            revised = True
    return revised

def select_unassigned_variable(do_mrv: bool, do_degree: bool = False) -> myVariable:  # Added do_degree parameter
    """
    Selects unassigned variable using MRV and optionally Degree heuristic.
    """
    if not do_mrv:
        return select_static_order_variable()
    
    # Find all unassigned variables
    unassigned = [v for v in my_variables if v.value is None]
    if not unassigned:
        return None

    # MRV first
    if do_mrv:
        min_domain = min(len(v.remaining_domain) for v in unassigned)
        candidates = [v for v in unassigned if len(v.remaining_domain) == min_domain]
        
        # Apply Degree heuristic if multiple candidates
        if do_degree and len(candidates) > 1:
            return max([(v, len(g.neighbors(v))) for v in candidates], key=lambda x: x[1])[0]
        return candidates[0]
    
    return select_static_order_variable()


def select_unassigned_variable1(do_mrv: bool) -> myVariable:
    if do_mrv:
        return minimum_remaining_values()
    else:
        return select_static_order_variable()
    

def minimum_remaining_values() -> myVariable:
    """
    Implements the MRV heuristic: selects the variable with the fewest remaining values.
    Returns the unassigned variable with the smallest domain (or None if all variables are assigned).
    """
    min_domain_size = float('inf')
    selected_var = None

    for var in my_variables:
        if var.value is None:  # Only consider unassigned variables
            domain_size = len(var.remaining_domain)
            if domain_size < min_domain_size:
                min_domain_size = domain_size
                selected_var = var
            # Early exit if domain size is 1 (optimal case)
            if domain_size == 1:
                break

    return selected_var

def minimum_remaining_values1() -> myVariable:
    """
    Returns a variable with the lowest remaining domain count.
    """
    # YOUR CODE
        
def order_domain_values(v: myVariable, do_lcv: bool) -> List[int]:
    if do_lcv:
        return least_constraining_value(v)
    else:
        return static_order_domains(v)
    
def least_constraining_value(v: myVariable) -> List[int]:
    """
    Orders domain values by the Least Constraining Value (LCV) heuristic.
    Returns values sorted by how few options they remove from neighboring variables.
    """
    value_scores = []
    
    for value in v.remaining_domain:
        # Count how many values this would eliminate from neighbors' domains
        eliminations = 0
        for neighbor in g.neighbors(v):
            if neighbor.value is not None:
                continue  # Skip assigned neighbors
            for neighbor_value in neighbor.remaining_domain:
                if not g.is_arc_satisfied(v, neighbor, value, neighbor_value):
                    eliminations += 1
        value_scores.append((value, eliminations))
    
    # Sort by least eliminations first (ascending order)
    value_scores.sort(key=lambda x: x[1])
    return [value for value, _ in value_scores]

def least_constraining_value1(v: myVariable) -> List[int]:
    """
    Orders the values in the domain of `v` based on how few constraints they impose on neighboring variables.  
    Values that allow the most options for neighboring variables are prioritized.
    """
    # YOUR CODE

def extract_domains() -> Dict[myVariable, List[int]]:
    """
    Backups all the remaining domains of every variable and returns them.

    :return: The becked-up domains as a dictionary {v:[d]}.
    """
    backup_domains = {}
    for v in my_variables:
        backup_domains[v] = v.remaining_domain
    return backup_domains

def restore_domains(backup_domains: Dict[myVariable, List[int]]):
    """
    Sets back the remaining domains of every variable to their becked-up domains.

    :param backup_domains: The previous remaining_domains of all variables.
    """
    for v in my_variables:
        v.remaining_domain = backup_domains[v]

def set_doms_to_values():
    """
    Sets remaining_domain of all variables with assigned value to their value.

    Use this function after a variable has been assigned a value
    and inference() needs to be called.
    """
    for v in my_variables:
        if v.value is not None:
            v.remaining_domain = set([v.value])