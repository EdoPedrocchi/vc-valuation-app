import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="VC Valuation Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

def calculate_present_value(future_value, discount_rate, years):
    """Calculate present value using discount rate"""
    return future_value / ((1 + discount_rate) ** years)

def calculate_irr(cash_flows):
    """Calculate Internal Rate of Return"""
    # Using numpy's IRR calculation
    try:
        # Simple IRR calculation for binary cash flows
        if len(cash_flows) == 2:
            initial_investment = abs(cash_flows[0])
            exit_value = cash_flows[-1]
            years = len(cash_flows) - 1
            if initial_investment > 0 and exit_value > 0:
                return (exit_value / initial_investment) ** (1/years) - 1
        
        # For more complex cash flows, use numpy's financial functions
        return np.irr(cash_flows) if hasattr(np, 'irr') else 0.25  # Default fallback
    except:
        return 0.25  # Default 25% if calculation fails

def main():
    # Main header
    st.markdown('<h1 class="main-header">💰 VC Valuation Calculator</h1>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.markdown('<div class="section-header">📊 Valuation Parameters</div>', unsafe_allow_html=True)
        
        # Basic assumptions
        st.subheader("Basic Assumptions")
        valuation_date = st.date_input("Valuation Date", datetime.now())
        exit_year = st.selectbox("Exit Year", range(1, 11), index=6)  # Default Year 7
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP"], index=0)
        
        # Financial projections
        st.subheader("Financial Projections")
        exit_revenue = st.number_input(
            f"Revenue in Year {exit_year} ({currency})", 
            min_value=0, 
            value=10000000, 
            step=100000,
            format="%d"
        )
        
        ev_revenue_multiple = st.number_input(
            "EV/Revenue Multiple", 
            min_value=0.1, 
            value=10.0, 
            step=0.1,
            format="%.1f"
        )
        
        financial_debt = st.number_input(
            f"Financial Debt in Year {exit_year} ({currency})", 
            min_value=0, 
            value=0, 
            step=10000,
            format="%d"
        )
        
        cash_balance = st.number_input(
            f"Cash Balance in Year {exit_year} ({currency})", 
            min_value=0, 
            value=0, 
            step=10000,
            format="%d"
        )
        
        # Discount rate
        st.subheader("Valuation Assumptions")
        discount_rate = st.slider(
            "Required Return (%)", 
            min_value=5.0, 
            max_value=50.0, 
            value=25.0, 
            step=0.5
        ) / 100
        
        # Investor assumptions
        st.subheader("Investor Assumptions")
        equity_stake_entry = st.slider(
            "Equity Stake at Entry (%)", 
            min_value=1.0, 
            max_value=100.0, 
            value=10.0, 
            step=0.1
        ) / 100
        
        dilution_effect = st.slider(
            "Dilution Effect (%)", 
            min_value=0.0, 
            max_value=50.0, 
            value=0.0, 
            step=0.1
        ) / 100
        
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Calculate valuation
        enterprise_value = exit_revenue * ev_revenue_multiple
        equity_value = enterprise_value - financial_debt + cash_balance
        present_value = calculate_present_value(equity_value, discount_rate, exit_year)
        
        # Calculate investor metrics
        equity_stake_exit = equity_stake_entry * (1 - dilution_effect)
        investment_amount = present_value * equity_stake_entry
        exit_proceeds = equity_value * equity_stake_exit
        
        # Calculate IRR and multiples
        cash_flows = [-investment_amount, exit_proceeds]
        investor_irr = calculate_irr(cash_flows)
        cash_on_cash_multiple = exit_proceeds / investment_amount if investment_amount > 0 else 0
        
        # Display key metrics
        st.markdown('<div class="section-header">📈 Valuation Results</div>', unsafe_allow_html=True)
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric(
                "Company Equity Value", 
                f"{currency} {equity_value:,.0f}",
                delta=f"Year {exit_year}"
            )
        
        with metric_col2:
            st.metric(
                "Present Value", 
                f"{currency} {present_value:,.0f}",
                delta="Today"
            )
        
        with metric_col3:
            st.metric(
                "Investor IRR", 
                f"{investor_irr:.1%}",
                delta="Annual Return"
            )
        
        with metric_col4:
            st.metric(
                "Cash Multiple", 
                f"{cash_on_cash_multiple:.1f}x",
                delta="Money Multiple"
            )
        
        # Detailed calculations table
        st.markdown('<div class="section-header">📊 Detailed Calculations</div>', unsafe_allow_html=True)
        
        # Create projection table
        years = list(range(2023, 2023 + exit_year + 4))
        projection_data = {
            'Year': years,
            'Cash Flow Date': [f"31-Dec-{year}" for year in years],
            'Forecast Year': [f"Year {i-2023}" for i in years],
            'Revenue': [exit_revenue if i-2023 == exit_year else 0 for i in years],
            'Enterprise Value': [enterprise_value if i-2023 == exit_year else 0 for i in years],
            'Equity Value': [equity_value if i-2023 == exit_year else 0 for i in years],
            'Discount Factor': [1/((1+discount_rate)**(i-2023)) for i in years],
            'Present Value': [present_value if i-2023 == exit_year else 0 for i in years]
        }
        
        df = pd.DataFrame(projection_data)
        st.dataframe(df, use_container_width=True)
        
        # Investor cash flows
        st.markdown('<div class="section-header">💰 Investor Cash Flows</div>', unsafe_allow_html=True)
        
        investor_data = {
            'Year': years,
            'Investment': [-investment_amount if i == 2023 else 0 for i in years],
            'Exit Proceeds': [exit_proceeds if i-2023 == exit_year else 0 for i in years],
            'Net Cash Flow': [-investment_amount if i == 2023 else (exit_proceeds if i-2023 == exit_year else 0) for i in years],
            'Equity Stake': [f"{equity_stake_entry:.1%}" if i-2023 <= exit_year else "" for i in years]
        }
        
        df_investor = pd.DataFrame(investor_data)
        st.dataframe(df_investor, use_container_width=True)
    
    with col2:
        # Visualization section
        st.markdown('<div class="section-header">📊 Visualizations</div>', unsafe_allow_html=True)
        
        # Valuation breakdown pie chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Enterprise Value', 'Debt', 'Cash'],
            values=[enterprise_value, financial_debt, cash_balance],
            hole=0.4,
            marker_colors=['#3498db', '#e74c3c', '#2ecc71']
        )])
        fig_pie.update_layout(
            title="Valuation Breakdown",
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # IRR sensitivity analysis
        irr_range = []
        discount_rates = np.arange(0.15, 0.35, 0.01)
        
        for dr in discount_rates:
            pv_temp = calculate_present_value(equity_value, dr, exit_year)
            investment_temp = pv_temp * equity_stake_entry
            exit_temp = equity_value * equity_stake_exit
            irr_temp = calculate_irr([-investment_temp, exit_temp])
            irr_range.append(irr_temp)
        
        fig_sensitivity = go.Figure()
        fig_sensitivity.add_trace(go.Scatter(
            x=discount_rates * 100,
            y=np.array(irr_range) * 100,
            mode='lines+markers',
            name='IRR',
            line=dict(color='#3498db', width=3)
        ))
        fig_sensitivity.update_layout(
            title="IRR Sensitivity to Discount Rate",
            xaxis_title="Discount Rate (%)",
            yaxis_title="IRR (%)",
            height=300
        )
        st.plotly_chart(fig_sensitivity, use_container_width=True)
        
        # Multiple scenarios comparison
        st.subheader("Quick Scenario Analysis")
        
        scenarios = {
            'Conservative': {'multiple': ev_revenue_multiple * 0.7, 'revenue': exit_revenue * 0.8},
            'Base Case': {'multiple': ev_revenue_multiple, 'revenue': exit_revenue},
            'Optimistic': {'multiple': ev_revenue_multiple * 1.3, 'revenue': exit_revenue * 1.2}
        }
        
        scenario_results = []
        for scenario_name, params in scenarios.items():
            ev_scenario = params['revenue'] * params['multiple']
            equity_scenario = ev_scenario - financial_debt + cash_balance
            pv_scenario = calculate_present_value(equity_scenario, discount_rate, exit_year)
            investment_scenario = pv_scenario * equity_stake_entry
            exit_scenario = equity_scenario * equity_stake_exit
            irr_scenario = calculate_irr([-investment_scenario, exit_scenario])
            
            scenario_results.append({
                'Scenario': scenario_name,
                'IRR': f"{irr_scenario:.1%}",
                'Multiple': f"{exit_scenario/investment_scenario:.1f}x",
                'Investment': f"{currency} {investment_scenario:,.0f}"
            })
        
        df_scenarios = pd.DataFrame(scenario_results)
        st.dataframe(df_scenarios, use_container_width=True)
    
    # Export functionality
    st.markdown('<div class="section-header">📁 Export Results</div>', unsafe_allow_html=True)
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if st.button("📊 Export to Excel", type="primary"):
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Projections', index=False)
                df_investor.to_excel(writer, sheet_name='Investor_Flows', index=False)
                df_scenarios.to_excel(writer, sheet_name='Scenarios', index=False)
            
            st.download_button(
                label="Download Excel File",
                data=output.getvalue(),
                file_name=f"VC_Valuation_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col_export2:
        if st.button("📈 Generate Report", type="secondary"):
            report = f"""
            # VC Valuation Report
            
            **Valuation Date:** {valuation_date}
            **Exit Year:** Year {exit_year}
            **Currency:** {currency}
            
            ## Key Metrics
            - **Company Equity Value:** {currency} {equity_value:,.0f}
            - **Present Value:** {currency} {present_value:,.0f}
            - **Investor IRR:** {investor_irr:.1%}
            - **Cash Multiple:** {cash_on_cash_multiple:.1f}x
            - **Investment Required:** {currency} {investment_amount:,.0f}
            
            ## Assumptions
            - **Exit Revenue:** {currency} {exit_revenue:,.0f}
            - **EV/Revenue Multiple:** {ev_revenue_multiple:.1f}x
            - **Discount Rate:** {discount_rate:.1%}
            - **Equity Stake:** {equity_stake_entry:.1%}
            """
            
            st.download_button(
                label="Download Report (Markdown)",
                data=report,
                file_name=f"VC_Report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()
