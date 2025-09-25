import papermill as pm

# List of budgets and only_fallback values you want to try
budgets = [100, 200, 1000]
only_fallback_options = [True, False]

for budget in budgets:
    for only_fallback in only_fallback_options:
        output_notebook = f"worst_ncp_budget{budget}_fallback{only_fallback}.ipynb"
        pm.execute_notebook(
            'worst_ncp.ipynb',
            output_notebook,
            parameters={
                'budget_': budget,
                'only_fallback': only_fallback
            }
        )
        print(f"Run complete: {output_notebook}")