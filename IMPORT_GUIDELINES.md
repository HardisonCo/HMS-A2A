# Import Fix Guidelines

After the reorganization, you'll need to update imports in your Python files.
Here are some common patterns:

## Before:
```python
from common.utils import helper
import gov_agents.ustda_agent as ustda
from mac.economist_agent import EconomistAgent
```

## After:
```python
from src.common.utils import helper
import src.agents.gov.ustda_agent as ustda
from src.domains.economic.mac.economist_agent import EconomistAgent
```

## Tips for updating imports:
1. Use find & replace across the codebase
2. For each file, check its imports first before running it
3. Consider using relative imports in tests and examples

## Common replacements:
- `from common` → `from src.common`
- `from gov_agents` → `from src.agents.gov`
- `from mac` → `from src.domains.economic.mac`
- `from trade_balance` → `from src.domains.economic.trade`
- `from genetic_theorem_prover` → `from src.domains.ga`
