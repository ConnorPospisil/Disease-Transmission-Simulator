"""
Disease Transmission Simulator

An agent-based epidemiological model that simulates disease spread through
a population with diversified mixing, multiple interventions (vaccines,
masks, social isolation), and natural immunity buildup.

Author: pospsl
"""

from random import random, sample, randint, seed
from os.path import isfile
from os import access, R_OK
import matplotlib.pyplot as plt


def signed():
    """Return author identifier."""
    return ["pospsl"]


def flip(p=0.5):
    """
    Flip a weighted coin.
    
    Args:
        p (float): Probability of returning True (default: 0.5)
        
    Returns:
        bool: True if random value <= p, False otherwise
        
    Example:
        >>> flip(0.7)  # Returns True 70% of the time
        True
    """
    return random() <= p


def binnedSample(k, N):
    """
    Sample random integers from binned populations without replacement.
    
    This function supports three modes of operation:
    1. Both k and N are ints: Sample k values from range(N)
    2. k is int, N is tuple: Sample k values from bins defined by N
    3. Both are tuples: Sample k[i] values from each bin N[i]
    
    Args:
        k (int or tuple): Number of samples (or tuple of counts per bin)
        N (int or tuple): Population size (or tuple of bin sizes)
        
    Returns:
        set: Random integers sampled according to the specified mode
        
    Examples:
        >>> binnedSample(3, 15)
        {8, 9, 6}  # 3 samples from range 0-14
        
        >>> binnedSample(3, (5, 5, 5))
        {4, 3, 14}  # 3 samples from three bins of size 5 (0-4), (5-9), (10-14)
        
        >>> binnedSample((1, 1, 1), (5, 5, 5))
        {2, 6, 11}  # 1 sample from each bin
        
        >>> binnedSample((0, 0, 3), (5, 5, 5))
        {14, 12, 10}  # All 3 samples from the third bin
    """
    # Mode 1: Simple random sampling
    if type(k) is int and type(N) is int:
        return set(sample(range(N), k))
    
    # Mode 2: Sample from bins with total population sum(N)
    elif type(k) is int and type(N) is tuple:
        return set(sample(range(sum(N)), k))
    
    # Mode 3: Sample specified amounts from each bin
    elif type(k) is tuple and type(N) is tuple and len(k) == len(N):
        samples = []
        # Iterate through each bin
        for i in range(len(k)):
            # Calculate the range for this bin (builds on previous bins)
            bin_start = sum(N[0:i+1]) - N[i]
            bin_end = sum(N[0:i+1])
            # Sample k[i] values from this bin's range
            samples += sample(range(bin_start, bin_end), k[i])
        return set(samples)
    
    else:
        print('Warning: Invalid arguments to binnedSample')
        return set()


def newPop(config):
    """
    Create a new population of agents with initial disease states.
    
    Each agent is represented as a dictionary with keys:
    - 'state': Disease state (-1=susceptible, 0=recovered, >0=infected countdown)
    - 'vaccine': Vaccine effectiveness (0.0-1.0, 0 if unvaccinated)
    - 'mask': Masking effectiveness (0.0-1.0, 0 if not masking)
    - 'natural_immunity': Immunity from prior infections (0.0-1.0)
    - 'type': Subgroup identifier (only if N is a tuple)
    - 'sociso': Social isolation adherence (0.0-1.0, set when infected)
    
    Args:
        config (dict): Configuration dictionary containing:
            - N (int or tuple): Population size(s)
            - I (int or tuple): Initial infected count(s)
            - vp (float): Vaccination probability
            - mp (float): Masking probability
            - ap (float): Asymptomatic probability
            - ip (float): Isolation probability
            - di (int): Days in infected state
            - de (int): Days in exposed state
            
    Returns:
        tuple: (population, infected_set) where:
            - population is a tuple of agent dictionaries
            - infected_set is a set of indices of initially infected agents
    """
    def helper(p):
        """
        Return random effectiveness value with probability p, else 0.
        
        This helper implements a choice-then-effectiveness pattern:
        with probability p, the agent adopts the behavior and gets
        a random effectiveness (0-1); otherwise they don't adopt it (0).
        """
        return (flip(p) and random()) or 0

    # Create population based on structure (homogeneous or subgroups)
    if type(config['N']) is tuple:
        # Diverse population with subgroups
        pop = tuple([
            {
                'state': -1,
                'vaccine': helper(config['vp']),
                'mask': helper(config['mp']),
                'natural_immunity': 0.0,
                'type': subgroup_id
            }
            for subgroup_id in range(len(config['N']))
            for _ in range(config['N'][subgroup_id])
        ])
    else:
        # Homogeneous population
        pop = tuple([
            {
                'state': -1,
                'vaccine': helper(config['vp']),
                'mask': helper(config['mp']),
                'natural_immunity': 0.0
            }
            for _ in range(config['N'])
        ])

    # Select initial infected agents using binned sampling
    inf = binnedSample(config['I'], config['N'])
    
    # Set initial infected states and social isolation
    for i in inf:
        # Set infection countdown (will be decremented on first update)
        pop[i]['state'] = config['di'] + config['de'] + 1
        
        # Determine social isolation behavior
        if flip(config['ap']):
            # Asymptomatic agents don't know to isolate
            pop[i]['sociso'] = 0.0
        else:
            # Symptomatic agents may choose to isolate
            pop[i]['sociso'] = helper(config['ip'])

    return (pop, inf)


def update(pop, inf, config):
    """
    Update agent disease states at the beginning of each simulation day.
    
    This function:
    1. Decrements infection counters for all infected agents
    2. Transitions agents at the end of infection to recovered or susceptible
    3. Grants natural immunity to agents who become susceptible after infection
    
    Args:
        pop (tuple): Population of agent dictionaries
        inf (set): Set of currently infected agent indices
        config (dict): Configuration with 'rp' (recovery probability)
        
    Returns:
        set: Updated set of currently infected agent indices
        
    Notes:
        Agents with state=1 (end of infection) either:
        - Recover with full immunity (state=0) with probability rp
        - Become susceptible again (state=-1) with probability (1-rp),
          but gain natural immunity from the infection
    """
    drop = set()  # Agents who recover or become susceptible this round
    
    for i in inf:
        if pop[i]['state'] == 1:
            # Agent at end of infectious period
            if flip(1 - config['rp']):
                # Become susceptible again (reinfection possible)
                pop[i]['state'] = -1
                # Grant natural immunity from this infection
                # Each infection adds 0-0.5 immunity, capped at 0.9
                pop[i]['natural_immunity'] = min(
                    0.9,
                    pop[i]['natural_immunity'] + random() * 0.5
                )
            else:
                # Recover with full immunity
                pop[i]['state'] = 0
            
            drop.add(i)
            
        elif pop[i]['state'] > 0:
            # Still infectious, decrement countdown
            pop[i]['state'] -= 1
    
    # Remove recovered/susceptible agents from infected set
    return inf - drop


def readConfig(cfile):
    """
    Read simulation configuration from file.
    
    Args:
        cfile (str): Path to configuration file
        
    Returns:
        dict: Configuration dictionary with all parameters
        
    Configuration File Format:
        - Lines starting with '#' are comments
        - Format: parameter: value  # optional comment
        - Supports integers, floats, booleans, and comma-separated tuples
        - Mixing parameters use integer keys (0, 1, 2, ...) for subgroups
        
    Default Configuration:
        If file doesn't exist or parameter is missing, defaults are used:
        - N=100, I=1, m=4, de=3, di=5
        - tpe=0.01, tpi=0.02, rp=0.5
        - vp=0.9, mp=0.3, ap=0.3, ip=0.4
        - max=100, verbose=False
    """
    def cast(value):
        """Convert string value to appropriate type (bool, int, float, or tuple)."""
        # Check for boolean
        if isinstance(value, str) and value.lower() in ("true", "false"):
            return value.lower().capitalize() == 'True'
        
        # Check for comma-separated tuple
        elif len(value.strip().split(',')) > 1:
            parts = [int(v) for v in value.strip().split(',')]
            return tuple(parts)
        
        # Check for integer
        elif value.isnumeric():
            return int(value)
        
        # Check for float
        elif ''.join(value.split('.')).isnumeric():
            return float(value)
        
        else:
            print(f"Unexpected value '{value}' in configuration file.")
            return None

    # Default configuration
    config = {
        'N': 100, 'I': 1, 'm': 4, 'de': 3, 'di': 5,
        'tpe': 0.01, 'tpi': 0.02, 'rp': 0.5,
        'vp': 0.9, 'mp': 0.3, 'ap': 0.3, 'ip': 0.4,
        'max': 100, 'verbose': False, 'seed': seed()
    }

    # Read configuration file if it exists
    if isfile(cfile) and access(cfile, R_OK):
        with open(cfile, 'r') as file:
            for line in file:
                # Skip blank lines and comments
                if line.strip() == '' or line.lstrip()[0] == '#':
                    continue
                
                # Parse line: split on ':' and extract key/value
                parts = [element.strip() for element in line.split(':')]
                
                # Standard configuration parameter
                if parts[0] in config.keys():
                    config[parts[0]] = cast(parts[1].split('#')[0].strip())
                
                # Mixing parameter for subgroup (integer key)
                elif parts[0].isdigit() and int(parts[0]) < len(config['N']):
                    config[int(parts[0])] = cast(parts[1].split('#')[0].strip())
                
                else:
                    print(f"Unexpected line '{parts[0]}' in configuration file.")
    
    return config


def plotCurve(curve, config, stats=None):
    """
    Create visualization of epidemic curve.
    
    Generates a professional graph showing active infections over time,
    with peak marked and summary statistics displayed.
    
    Args:
        curve (list): Daily infection counts
        config (dict): Configuration dictionary (for population size)
        stats (dict, optional): Statistics to display:
            - 'attack_rate': Percentage of population infected
            - 'totinf': Total infection events
            - 'reinfections': Number of reinfections
            
    Output:
        Saves 'epidemic_curve.png' in current directory
        
    Visualization Features:
        - Line plot with shaded area
        - Peak day/value marked
        - Statistics box with key metrics
        - High-resolution (300 DPI) output
    """
    plt.figure(figsize=(12, 6))
    
    days = list(range(len(curve)))
    
    # Plot main curve with shading
    plt.plot(days, curve, linewidth=2, color='#e74c3c', label='Active Infections')
    plt.fill_between(days, curve, alpha=0.3, color='#e74c3c')
    
    # Mark peak
    peak_day = curve.index(max(curve))
    peak_value = max(curve)
    plt.plot(peak_day, peak_value, 'o', markersize=10, color='darkred',
             label=f'Peak: {peak_value} on day {peak_day}')
    
    # Formatting
    plt.xlabel('Days', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Active Infections', fontsize=12, fontweight='bold')
    plt.title('Epidemic Curve - Disease Transmission Simulation',
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='upper right')
    
    # Add statistics text box
    if stats:
        total_pop = sum(config['N']) if type(config['N']) is tuple else config['N']
        textstr = '\n'.join([
            f"Duration: {len(curve)-1} days",
            f"Population: {total_pop}",
            f"Attack Rate: {stats['attack_rate']:.1f}%",
            f"Total Infections: {stats['totinf']}",
            f"Reinfections: {stats['reinfections']}"
        ])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    # Save figure with error handling
    import os
    output_path = 'epidemic_curve.png'
    
    try:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"\nWarning: Could not save visualization: {e}")
        print("(Continuing with simulation...)")


def sim(cfile='Example(Subgroups).cfg', visualize=True):
    """
    Run disease transmission simulation.
    
    This is the main simulation function that models epidemic spread through
    a population over time, tracking infections, interventions, and outcomes.
    
    Args:
        cfile (str): Path to configuration file (default: 'hw3.cfg')
        visualize (bool): Whether to generate epidemic curve visualization
        
    Returns:
        list: Epidemic curve showing daily active infection counts
        
    Simulation Process:
        1. Read configuration and create population
        2. Each day:
           - Update agent disease states
           - Infected agents interact with others based on mixing parameters
           - Transmission attempts based on disease state and protections
           - Track new infections and reinfections
        3. Continue until no infections remain or max days reached
        4. Report statistics and optionally generate visualization
        
    Disease State Model:
        - state = -1: Susceptible
        - state = 0: Recovered (immune)
        - state = 1 to di: Infected period (symptomatic)
        - state = di+1 to di+de: Exposed period (pre-symptomatic)
        
    Protection Layers:
        Agents are protected from infection by:
        1. Vaccination (checked on exposure)
        2. Masking (checked on exposure and when infectious)
        3. Natural immunity from prior infections
        4. Social isolation (reduces spreading when infectious)
        
    Output:
        Prints statistics including:
        - Duration of epidemic
        - Total infection events
        - Unique agents infected (attack rate)
        - Number of reinfections
    """
    def susceptible(i):
        """Check if agent i is susceptible to infection."""
        return (pop[i]['state'] == -1 and
                not flip(pop[i]['vaccine']) and
                not flip(pop[i]['mask']) and
                not flip(pop[i]['natural_immunity']))

    def exposed(i):
        """Check if agent i is in exposed state (infectious but pre-symptomatic)."""
        return config['di'] < pop[i]['state'] <= config['di'] + config['de']

    def infected(i):
        """Check if agent i is in infected state (symptomatic and infectious)."""
        return 0 < pop[i]['state'] <= config['di']

    def infectious(i):
        """Check if agent i can spread disease (exposed or infected, not masked/isolated)."""
        return (0 < pop[i]['state'] <= config['di'] + config['de'] and
                not flip(pop[i]['mask']) and
                not flip(pop[i]['sociso']))

    def recovered(i):
        """Check if agent i has recovered with immunity."""
        return pop[i]['state'] == 0

    # Initialize simulation
    config = readConfig(cfile)
    
    if 'seed' in config:
        seed(config['seed'])

    pop, inf = newPop(config)
    
    # Track statistics
    totinf = len(inf)  # Total infection events
    ever_infected = set(inf)  # Unique individuals infected
    curve = [totinf]  # Daily active infection counts

    # Main simulation loop
    rounds = 0
    while rounds < config['max']:
        # Beginning-of-day status update
        inf = update(pop, inf, config)
        curve.append(len(inf))

        if config['verbose']:
            print(f"Day {len(curve)-1}: {curve[-1]} of {len(pop)} agents infected.")

        # Check if epidemic has ended
        if curve[-1] == 0:
            # Calculate final statistics
            attack_rate = (100 * len(ever_infected)) / len(pop)
            reinfection_rate = totinf - len(ever_infected)
            
            print(f"Pandemic extinguished: {len(curve)-1} days, {totinf} total infection events.")
            print(f"  Unique agents infected: {len(ever_infected)} of {len(pop)} ({attack_rate:.1f}% attack rate)")
            if reinfection_rate > 0:
                print(f"  Reinfections: {reinfection_rate} ({(100*reinfection_rate)/totinf:.1f}% of total events)")
            
            # Generate visualization
            if visualize:
                stats = {
                    'attack_rate': attack_rate,
                    'totinf': totinf,
                    'reinfections': reinfection_rate
                }
                plotCurve(curve, config, stats)
            
            break

        # Transmission phase: infected agents interact with others
        newinf = set()
        for i in inf:
            # Determine who agent i interacts with today
            if type(config['N']) is tuple:
                # Heterogeneous mixing based on agent's subgroup
                num_interactions = randint(0, config['m'])
                # Calculate interactions per subgroup based on mixing matrix
                interactions_per_group = tuple([
                    round((num_interactions * pct) / 100)
                    for pct in config[pop[i]['type']]
                ])
                interactions = binnedSample(interactions_per_group, config['N'])
            else:
                # Homogeneous mixing
                interactions = sample(range(len(pop)), randint(0, config['m']))
            
            # Attempt transmission to each interaction
            for j in interactions:
                # Check all conditions for transmission
                if (infectious(i) and susceptible(j) and
                    ((exposed(i) and flip(config['tpe'])) or
                     (infected(i) and flip(config['tpi'])))):
                    
                    # New infection occurs
                    totinf += 1
                    ever_infected.add(j)
                    pop[j]['state'] = config['di'] + config['de'] + 1

                    # Set social isolation for newly infected agent
                    if flip(config['ap']):
                        # Asymptomatic - won't isolate
                        pop[j]['sociso'] = 0
                    else:
                        # Symptomatic - may choose to isolate
                        pop[j]['sociso'] = ((flip(config['ip']) and random()) or 0)

                    if config['verbose']:
                        print(f"  Agent {j} infected by agent {i} [si={pop[j]['sociso']:.2f}].")
                    
                    newinf.add(j)

        # Add new infections to active set
        inf.update(newinf)
        rounds += 1
    
    else:
        # Simulation reached max rounds without extinction
        attack_rate = (100 * len(ever_infected)) / len(pop)
        reinfection_rate = totinf - len(ever_infected)
        
        print(f"Pandemic persists: {len(curve)-1} days, {totinf} total infection events.")
        print(f"  Unique agents infected: {len(ever_infected)} of {len(pop)} ({attack_rate:.1f}% attack rate)")
        if reinfection_rate > 0:
            print(f"  Reinfections: {reinfection_rate} ({(100*reinfection_rate)/totinf:.1f}% of total events)")
        
        if visualize:
            stats = {
                'attack_rate': attack_rate,
                'totinf': totinf,
                'reinfections': reinfection_rate
            }
            plotCurve(curve, config, stats)
    
    return curve


if __name__ == "__main__":
    curve = sim()
    print("\nEpidemic curve (daily active infections):")
    print(curve)