# Disease Transmission Simulator

An agent-based epidemiological model that simulates disease spread through populations with heterogeneous mixing, multiple public health interventions, and realistic reinfection dynamics.

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-complete-success.svg)

---

## Overview

This simulator models how infectious diseases spread through populations over time, accounting for:
- **Heterogeneous population mixing** - Different subgroups (e.g., community, healthcare workers, nursing homes) interact at different rates
- **Multiple interventions** - Vaccination, masking, and social isolation with varying effectiveness
- **Natural immunity** - Progressive immunity buildup from prior infections
- **Reinfection dynamics** - Agents can be reinfected with decreasing probability based on exposure history
- **Professional visualization** - Automated generation of epidemic curves with key statistics

Originally developed as a course project for Introduction to Computer Science (CS1210), this simulator has been significantly enhanced beyond the original requirements to explore realistic epidemic scenarios and demonstrate software engineering best practices.

---

## Key Features

### Epidemiological Modeling
- **SEIR-like disease progression**: Susceptible → Exposed → Infected → Recovered/Susceptible
- **Configurable disease parameters**: Incubation period, infectious period, transmission rates
- **Dual recovery pathways**: Permanent immunity vs. susceptibility with partial protection
- **Natural immunity accumulation**: Each infection grants increasing resistance to reinfection

### Population Structure
- **Homogeneous populations**: Single well-mixed population
- **Heterogeneous subgroups**: Multiple interacting populations with custom mixing matrices
- **Bridge populations**: Model healthcare workers, essential workers, etc.
- **Isolated groups**: Simulate protected populations (nursing homes, quarantine)

### Public Health Interventions
- **Vaccination**: Variable uptake and effectiveness per individual
- **Masking**: Dual protection (source control + personal protection)
- **Social isolation**: Behavioral response to symptomatic infection
- **Intervention layering**: Multiple protections compound to reduce transmission

### Technical Highlights
- **Clean, documented code**: Professional docstrings following PEP 257 standards
- **Configurable scenarios**: External configuration files for reproducible experiments
- **Automated visualization**: Publication-quality epidemic curves with matplotlib
- **Modular design**: Clear separation of concerns for easy modification

---

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/[your-username]/disease-transmission-simulator.git
   cd disease-transmission-simulator
   ```
   *(Replace `[your-username]` with your GitHub username)*

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

**Run with default configuration:**
```python
python simulator.py
```

**Run with a specific scenario:**
```python
# In Python
from simulator import sim

# Run baseline epidemic
curve = sim('configs/example_baseline.cfg')

# Run high-intervention scenario
curve = sim('configs/example_high_intervention.cfg')

# Run without visualization
curve = sim('configs/default.cfg', visualize=False)
```

**Command-line usage:**
```bash
python -c "from simulator import sim; sim('configs/example_baseline.cfg')"
```

### Output

The simulator produces:
1. **Console statistics**: Attack rate, total infections, reinfection count, duration
2. **Epidemic curve**: List of daily active infection counts
3. **Visualization**: `epidemic_curve.png` with annotated graph and statistics box

---

## Example Scenarios

The simulator includes four pre-configured scenarios designed to compare different epidemic conditions systematically:

### 1. Default Scenario (`DiseaseSim.cfg`)
Baseline epidemic with subgroup structure and moderate interventions.

**Configuration:**
- **Population**: 4 subgroups (50, 30, 10, 10) with custom mixing matrix
- **Interventions**: Low vaccination (21%), moderate masking (30%)
- **Transmission**: Moderate-high (50% exposed, 50% infected)
- **Recovery immunity**: 50%

**Mixing Matrix:**
```
Group 0: 50% internal, 40% group 1, 10% group 2
Group 1: 40% group 0, 50% internal, 10% group 2  
Group 2: 80% group 0, 10% group 1, 10% group 3
Group 3: 100% internal (completely isolated)
```

**Use Case:** Baseline for comparing intervention effects and disease parameters.

---

### 2. High Intervention (`Example(High Intervention).cfg`)
Testing the impact of strong public health response.

**Configuration:**
- **Population**: 100 agents (homogeneous) - simplified for clearer intervention effects
- **Interventions**: HIGH vaccination (80%), HIGH masking (70%), HIGH isolation (80%)
- **Transmission**: Reasonably high (50% exposed, 70% infected)
- **Recovery immunity**: 20% (allows more reinfections)
- **Contact rate**: Reduced (0-4 vs. 0-5 default)

**Key Differences from Default:**
- ↑ Vaccination: 21% → 80%
- ↑ Masking: 30% → 70%  
- ↑ Isolation: (none) → 80%
- ↓ Contacts: 5 → 4

**Expected Outcome:**
- Attack rate: Lower than default despite comparable transmission rates
- Demonstrates compound protection effect
- Flattened, prolonged curve

**Use Case:** Quantifying intervention effectiveness - shows what happens when public health measures are widely adopted.

---

### 3. Highly Infectious Disease (`Example(Highly Infectious).cfg`)
Worst-case scenario: very contagious disease with low intervention adoption.

**Configuration:**
- **Population**: 100 agents (homogeneous)
- **Interventions**: LOW vaccination (60%), LOW masking (30%), LOW isolation (30%)
- **Transmission**: VERY HIGH (70% exposed, 85% infected)
- **Recovery immunity**: 20% (high reinfection rate)
- **Contact rate**: High (0-8)
- **Initial infections**: 5 (vs. 2-3 in other scenarios)

**Key Differences:**
- ↑ Transmission: 50% → 70-85%
- ↑ Contacts: 5 → 8
- ↓ Recovery immunity: Same as intervention scenario but overwhelmed by transmission

**Expected Outcome:**
- Attack rate: >90%
- Rapid exponential growth
- Burns out quickly (20-30 days)
- High reinfection count

**Use Case:** Understanding epidemic potential of highly contagious diseases (measles, early COVID variants). Shows intervention limits.

---

### 4. High Intervention + High Infectivity (`Example(High Intervention and Infectivity).cfg`)
**Critical comparison scenario:** Can strong interventions control a highly infectious disease?

**Configuration:**
- **Population**: 100 agents (homogeneous)
- **Interventions**: HIGH vaccination (80%), HIGH masking (70%), HIGH isolation (80%)
- **Transmission**: VERY HIGH (70% exposed, 85% infected) - same as highly infectious scenario
- **Recovery immunity**: 20%
- **Contact rate**: High (0-8) - same as highly infectious scenario

**Key Insight:** This scenario uses the SAME disease parameters as "Highly Infectious" but with the SAME interventions as "High Intervention." This allows direct comparison:
- Does high vaccination/masking matter against a very contagious disease?
- How much can interventions reduce the attack rate?

**Expected Outcome:**
- Attack rate: Still high but lower than scenario #3
- Slower spread than unmitigated scenario
- Earlier die-out due to higher immunity levels
- Demonstrates that interventions help but cannot eliminate highly infectious diseases

**Use Case:** Policy analysis - understanding realistic expectations for intervention effectiveness against different disease types.

---

### 5. Subgroups/Nursing Home (`Example(Subgroups).cfg`)
Heterogeneous mixing with vulnerable populations.

**Configuration:**
- **Population**: 4 subgroups (60, 20, 15, 5) - Community, Healthcare, Nursing Home, Hospital
- **Interventions**: Moderate vaccination (40%), high masking (60%)
- **Transmission**: Moderate exposed (35%), VERY HIGH infected (99%)
- **Recovery immunity**: 20%
- **Mixing matrix**: Models isolation of vulnerable groups

**Mixing Matrix:**
```
From → To    Community  Healthcare  Nursing Home  Hospital
Community        70%        20%          5%          5%
Healthcare       30%        40%         25%          5%
Nursing Home     10%        30%         60%          0%
Hospital          0%        50%          0%         50%
```

**Key Features:**
- Healthcare workers act as bridge population
- Nursing home has 60% internal mixing (partial isolation)
- Hospital completely isolated from community (0% interaction)

**Expected Outcome:**
- Variable attack rates across groups
- Healthcare workers: High exposure (bridge effect)
- Nursing home: Partially protected by isolation
- Hospital: Protected by complete isolation

**Use Case:** Exploring targeted protection strategies. Shows how population structure and selective isolation can protect vulnerable groups without economy-wide lockdowns.

---

## Scenario Comparison Table

This experimental design allows systematic comparison of intervention and disease effects:

| Scenario | Population | Vaccination | Masking | Transmission | Contacts | Purpose |
|----------|------------|-------------|---------|--------------|----------|---------|
| **Default** | 100 (4 groups) | 21% | 30% | 50%/50% | 0-5 | Baseline |
| **High Intervention** | 100 | 80% | 70% | 50%/70% | 0-4 | Test intervention effect |
| **Highly Infectious** | 100 | 60% | 30% | 70%/85% | 0-8 | Test disease severity |
| **High Int. + High Inf.** | 100 | 80% | 70% | 70%/85% | 0-8 | Can interventions control severe disease? |
| **Subgroups** | 100 (4 groups) | 40% | 60% | 35%/99% | 0-6 | Test targeted protection |

**Key Comparisons:**
- **Intervention effect**: Compare scenarios #1 vs #2 (same transmission, different interventions)
- **Disease severity**: Compare scenarios #2 vs #3 (different transmission rates)
- **Intervention limits**: Compare scenarios #3 vs #4 (same disease, different interventions)
- **Targeted protection**: Scenario #5 shows an alternative to population-wide measures

---

## How It Works

### Disease Model

The simulator uses a modified SEIR (Susceptible-Exposed-Infected-Recovered) model with reinfection:

```
Susceptible → Exposed → Infected → Recovered (immune)
     ↑                                 ↓
     └──────────────────────────────────
              (with natural immunity)
```

**Agent States:**
- **Susceptible (-1)**: Can be infected (subject to intervention protections)
- **Recovered (0)**: Permanently immune, cannot be reinfected
- **Infected (1 to di)**: Symptomatic and infectious
- **Exposed (di+1 to di+de)**: Pre-symptomatic but infectious

### Intervention Mechanics

**Multi-layer protection model:**

Each transmission attempt must pass through multiple protection layers:

1. **Infectious agent's mask**: Reduces probability of spreading (source control)
2. **Infectious agent's isolation**: Reduces contact frequency when symptomatic
3. **Susceptible agent's vaccine**: Probabilistic protection from infection
4. **Susceptible agent's mask**: Reduces probability of exposure
5. **Susceptible agent's natural immunity**: Protection from prior infections

**Example:** An agent with 80% vaccine effectiveness, 60% mask effectiveness, and 50% natural immunity has:
```
P(infection) = P(transmission) × (1-0.8) × (1-0.6) × (1-0.5)
             = P(transmission) × 0.2 × 0.4 × 0.5
             = P(transmission) × 0.04  (96% total protection)
```

### Natural Immunity System

**Key Innovation:** Agents who recover and become susceptible again retain partial immunity.

**How it works:**
1. Agent gets infected for the first time
2. On recovery, with probability `rp` → Permanent immunity (state = 0)
3. Otherwise → Susceptible again (state = -1) BUT gains natural immunity (0-0.5)
4. If reinfected, immunity stacks (capped at 0.9)

**Impact:** Reinfection rates decrease over time as population immunity builds, creating more realistic epidemic dynamics.

---

## Configuration Guide

### File Format

Configuration files use a simple `key: value` format with comments:

```
# Comment lines start with #
parameter: value  # Inline comments supported

# For subgroups, use integer keys for mixing matrices
0: 50, 30, 20     # Group 0's mixing percentages
```

### Core Parameters

**Population Structure:**
- `N`: Population size (int for homogeneous, tuple for subgroups)
- `I`: Initial infected count (must match N structure)

**Disease Characteristics:**
- `de`: Days in exposed period (integer)
- `di`: Days in infected period (integer)
- `tpe`: Transmission probability when exposed (0.0-1.0)
- `tpi`: Transmission probability when infected (0.0-1.0)
- `rp`: Recovery probability for permanent immunity (0.0-1.0)

**Interventions:**
- `vp`: Probability of vaccination (0.0-1.0)
- `mp`: Probability of masking (0.0-1.0)
- `ap`: Probability of being asymptomatic (0.0-1.0)
- `ip`: Probability of social isolation when symptomatic (0.0-1.0)

**Behavioral:**
- `m`: Maximum daily contacts per agent (integer)

**Simulation Control:**
- `max`: Maximum simulation days (failsafe limit)
- `verbose`: Enable detailed daily output (True/False)
- `seed`: Random seed for reproducibility (optional)

**Mixing Matrix** (for subgroups only):
```
0: 60, 30, 10     # Group 0: 60% internal, 30% with group 1, 10% with group 2
1: 40, 50, 10     # Group 1: 40% with group 0, 50% internal, 10% with group 2
2: 20, 20, 60     # Group 2: 20% each with groups 0 & 1, 60% internal
```
Each row must sum to 100 (percentages).

### Creating Custom Scenarios

1. Copy an example config file
2. Modify parameters to match your scenario
3. Run: `sim('configs/your_scenario.cfg')`

**Tips:**
- Increase transmission rates (`tpe`, `tpi`) for more infectious diseases
- Decrease recovery probability (`rp`) for higher reinfection rates
- Use subgroups to model age stratification, geographic regions, or occupational groups
- Adjust mixing matrices to model isolation, lockdowns, or travel restrictions

---

## Project Structure

```
disease-transmission-simulator/
│
├── simulator.py              # Main simulation code
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
│
├── configs/                  # Configuration files
│   ├── default.cfg           # Default configuration
│   ├── example_baseline.cfg
│   ├── example_high_intervention.cfg
│   ├── example_subgroups.cfg
│   └── example_highly_infectious.cfg
│
├── docs/                     # Additional documentation
│   ├── ENHANCEMENTS_SUMMARY.md        # Detailed change log
│   ├── EXAMPLE_CONFIGS_README.md      # Config file guide
│   └── DOCUMENTATION_REFACTORING.md   # Code documentation standards
│
└── examples/                 # Sample outputs
    └── epidemic_curve_sample.png
```

---

## Enhancements Beyond Original Project

This simulator began as a homework assignment for CS1210 (Introduction to Computer Science) but has been significantly extended:

### Original Assignment Features
- Basic SEIR disease model
- Vaccination and masking interventions
- Single homogeneous population
- Configurable parameters

### Added Enhancements

**1. Heterogeneous Population Mixing**
- Multiple interacting subgroups with custom mixing matrices
- Enables modeling of realistic population structures (communities, workplaces, institutions)
- Demonstrates how isolation can protect vulnerable populations

**2. Natural Immunity System**
- Progressive immunity buildup from repeated infections
- Decreasing reinfection probability over time
- More realistic long-term epidemic dynamics

**3. Enhanced Tracking & Statistics**
- Distinction between total infection events and unique individuals infected
- Accurate attack rate calculation (fixed from >100% bug)
- Reinfection tracking and reporting

**4. Professional Visualization**
- Automated epidemic curve generation
- Annotated peak markers
- Embedded statistics
- Publication-quality output (300 DPI)

**5. Code Quality Improvements**
- Professional docstrings following PEP 257 standards
- Comprehensive inline documentation
- Modular function design
- Clear variable naming

**6. Example Scenarios**
- Four diverse, well-documented scenarios
- Demonstrates simulator capabilities
- Provides starting points for experimentation

---

## Sample Output

**Console Output:**
```
Pandemic extinguished: 48 days, 118 total infection events.
  Unique agents infected: 83 of 100 (83.0% attack rate)
  Reinfections: 35 (29.7% of total events)

Visualization saved to: epidemic_curve.png

Epidemic curve (daily active infections):
[3, 3, 4, 8, 9, 12, 22, 32, 39, 45, 51, 51, 59, 59, 50, 43, ...]
```

**Epidemic Curve Visualization:**

The simulator automatically generates a professional graph showing:
- Active infections over time (red line with shaded area)
- Peak infection day and count (marked with a red dot)
- Summary statistics in an embedded text box
- High-resolution output (300 DPI) saved as `epidemic_curve.png`

*Run the simulator to generate your own epidemic curve visualization!*

---

## Technical Challenges Overcome

### 1. Subgroup Integration
**Challenge:** Extending a homogeneous population model to support heterogeneous mixing without breaking existing functionality.

**Solution:** 
- Implemented `binnedSample()` function with three operational modes
- Used tuple-based configuration to maintain backward compatibility
- Created flexible mixing matrix system using integer dictionary keys

### 2. Reinfection Logic Debugging
**Challenge:** Attack rates exceeding 100% indicated reinfections being counted incorrectly.

**Solution:**
- Separated tracking of total infection events vs. unique individuals
- Added `ever_infected` set to track distinct agents
- Corrected attack rate calculation to use unique individuals

### 3. Natural Immunity Implementation
**Challenge:** Agents who recovered and became susceptible had no protection from prior infections, leading to unrealistic reinfection rates.

**Solution:**
- Added `natural_immunity` attribute to agent state
- Implemented stacking immunity system (capped at 0.9)
- Integrated immunity check into `susceptible()` function alongside other protections

---

## What I Learned

This project provided hands-on experience with:

- **Agent-based modeling**: Understanding how individual behaviors create population-level phenomena
- **Epidemiological concepts**: Disease progression, interventions, attack rates, epidemic curves
- **Data structures**: Using dictionaries, sets, and tuples to represent complex agent states
- **Algorithm design**: Creating flexible sampling functions that handle multiple input types
- **Scientific computing**: Using matplotlib for professional visualization
- **Software engineering**: Writing clean, documented, maintainable code
- **Debugging complex systems**: Tracking down subtle bugs in stochastic simulations
- **Configuration-driven design**: Separating code from parameters for flexibility

This was my first significant "data analysis" project, and it sparked an interest in how programming can model and understand complex real-world systems.

---

## Requirements

- Python 3.x
- matplotlib >= 3.5.0

Install with:
```bash
pip install -r requirements.txt
```

---

## Usage Tips

**For reproducible results:**
```python
# Set a seed in your config file
seed: 12345
```

**For detailed daily output:**
```python
# Set verbose in your config file
verbose: True
```

**For parameter sweeps:**
```python
# Run multiple scenarios and compare
scenarios = ['baseline', 'high_intervention', 'highly_infectious']
results = {s: sim(f'configs/example_{s}.cfg', visualize=False) for s in scenarios}

# Compare peak infections
for scenario, curve in results.items():
    print(f"{scenario}: Peak = {max(curve)} on day {curve.index(max(curve))}")
```

---

## Future Enhancements (Potential)

While the current simulator is feature-complete for its scope, potential extensions could include:

- **Age-stratified mortality**: Different outcomes by demographic group
- **Network visualization**: Animated transmission chains
- **Spatial component**: Geographic spread modeling
- **Parameter optimization**: Finding intervention strategies that minimize attack rate
- **Multi-strain dynamics**: Competing disease variants
- **Economic impact modeling**: Cost-benefit analysis of interventions

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Author

**Connor** (pospsl)  
Computer Science Student  
*Developed as an enhanced final project for CS1210: Introduction to Computer Science*

---

## Acknowledgments

- Original course project framework from CS1210
- Epidemiological model concepts inspired by standard SEIR models
- Matplotlib for visualization capabilities
- Thanks to the instructors and TAs who provided the foundational assignment

---

## Contact

Questions, suggestions, or collaboration opportunities? Feel free to reach out or open an issue!

---

*This simulator is for educational and demonstration purposes. It is a simplified model and should not be used for actual public health decision-making.*
