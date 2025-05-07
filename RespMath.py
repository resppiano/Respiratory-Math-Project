"""
Respiratory Therapy Oxygen Calculator.

This module provides functionality to calculate oxygen percentages based on flow rates
and display the results in a Streamlit web interface.
"""

from typing import Tuple, Dict, List, Optional
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Constants
ROOM_AIR_O2_PERCENTAGE: float = 21.0
MAX_O2_PERCENTAGE: float = 100.0
O2_INCREMENT_PER_LPM: float = 4.0
MAX_FLOW_RATE: float = 50.0
MIN_FLOW_RATE: float = 0.0

# Device flow rate ranges
DEVICE_RANGES: Dict[str, Dict[str, float]] = {
    "Nasal Cannula": {"min": 0, "max": 6},
    "Simple Mask": {"min": 6, "max": 10},
    "Non-rebreather/Partial Rebreather Mask": {"min": 10, "max": 15},
    "High Flow System": {"min": 15, "max": float("inf")}
}

def validate_flow_rate(flow_rate: float) -> float:
    """
    Validate and sanitize the flow rate input.
    
    Args:
        flow_rate (float): The flow rate to validate
        
    Returns:
        float: The validated flow rate
        
    Raises:
        ValueError: If the flow rate is invalid
    """
    try:
        flow_rate = float(flow_rate)
    except (TypeError, ValueError):
        raise ValueError("Flow rate must be a valid number")
    
    if not isinstance(flow_rate, (int, float)):
        raise ValueError("Flow rate must be a numeric value")
    
    if flow_rate < MIN_FLOW_RATE:
        raise ValueError(f"Flow rate cannot be negative. Minimum value is {MIN_FLOW_RATE}")
    
    if flow_rate > MAX_FLOW_RATE:
        raise ValueError(f"Flow rate cannot exceed {MAX_FLOW_RATE} LPM")
    
    return flow_rate

def round_to_one_decimal(value: float) -> float:
    """
    Round a float value to one decimal place using proper rounding rules.
    
    Args:
        value (float): The value to round
        
    Returns:
        float: Rounded value to one decimal place
    """
    try:
        return float(Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    except (TypeError, ValueError, decimal.InvalidOperation):
        return round(value, 1)

def calculate_oxygen_percentage(flow_rate_lpm: float) -> Tuple[float, str]:
    """
    Calculate approximate oxygen percentage based on flow rate in liters per minute (LPM).

    Args:
        flow_rate_lpm (float): Flow rate in liters per minute.

    Returns:
        Tuple[float, str]: A tuple containing:
            - Estimated oxygen percentage
            - Recommended delivery device

    Raises:
        ValueError: If flow_rate_lpm is invalid
    """
    flow_rate_lpm = validate_flow_rate(flow_rate_lpm)

    if flow_rate_lpm <= 0:
        return ROOM_AIR_O2_PERCENTAGE, "No supplemental oxygen (room air)"

    try:
        # Determine device and calculate percentage based on flow rate
        for device, range_dict in DEVICE_RANGES.items():
            if range_dict["min"] < flow_rate_lpm <= range_dict["max"]:
                if device == "Nasal Cannula":
                    estimated_percentage = ROOM_AIR_O2_PERCENTAGE + (flow_rate_lpm * O2_INCREMENT_PER_LPM)
                elif device == "Simple Mask":
                    estimated_percentage = 40 + ((flow_rate_lpm - 5) * O2_INCREMENT_PER_LPM)
                elif device == "Non-rebreather/Partial Rebreather Mask":
                    estimated_percentage = 60 + ((flow_rate_lpm - 10) * 3)
                else:  # High Flow System
                    estimated_percentage = 90

                return round_to_one_decimal(min(estimated_percentage, MAX_O2_PERCENTAGE)), device

        return MAX_O2_PERCENTAGE, "High Flow System or Venturi Mask"
    except Exception as e:
        st.error(f"Error calculating oxygen percentage: {str(e)}")
        return ROOM_AIR_O2_PERCENTAGE, "Error in calculation"

def create_gauge_chart(o2_percentage: float) -> Optional[plt.Figure]:
    """
    Create a gauge chart visualization for oxygen percentage.

    Args:
        o2_percentage (float): The calculated oxygen percentage.

    Returns:
        Optional[plt.Figure]: Matplotlib figure object containing the gauge chart,
                            or None if an error occurs.
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Create gauge chart
        ax.barh([0], [100], color='lightgray', height=0.5)
        ax.barh([0], [o2_percentage], color='#0066cc', height=0.5)
        
        # Configure axis
        ax.set_yticks([])
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 21, 40, 60, 80, 100])
        ax.set_xticklabels(['0%', '21%\n(Room Air)', '40%', '60%', '80%', '100%'])
        
        # Add percentage text
        ax.text(o2_percentage, 0, f"{o2_percentage:.1f}%", 
                ha='center', va='center', fontsize=14, 
                fontweight='bold', color='white',
                bbox=dict(facecolor='#0066cc', alpha=0.8, boxstyle='round,pad=0.5'))
        
        ax.set_title("Approximate O₂ Percentage", fontsize=14)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        return fig
    except Exception as e:
        st.error(f"Error creating gauge chart: {str(e)}")
        return None
    finally:
        plt.close('all')  # Clean up any remaining figures

def generate_reference_table() -> pd.DataFrame:
    """
    Generate a reference table of common flow rates and their corresponding oxygen percentages.

    Returns:
        pd.DataFrame: DataFrame containing the reference data.
    """
    try:
        flow_values = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15]
        table_data: List[Dict[str, any]] = []
        
        for flow in flow_values:
            try:
                percentage, dev = calculate_oxygen_percentage(flow)
                table_data.append({
                    "Flow Rate (LPM)": flow,
                    "O₂ %": f"{percentage:.1f}%",
                    "Device": dev.split(" (")[0]
                })
            except Exception as e:
                st.warning(f"Error calculating values for flow rate {flow}: {str(e)}")
                continue
        
        return pd.DataFrame(table_data)
    except Exception as e:
        st.error(f"Error generating reference table: {str(e)}")
        return pd.DataFrame()

def setup_page_config() -> None:
    """Configure the Streamlit page settings and custom CSS."""
    try:
        st.set_page_config(
            page_title="RT Oxygen Calculator",
            page_icon="🫁",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.markdown("""
            <style>
            .main-header {
                font-size: 2.5rem;
                color: #0066cc;
                text-align: center;
            }
            .subheader {
                font-size: 1.5rem;
                color: #444;
                text-align: center;
                margin-bottom: 2rem;
            }
            .result-container {
                background-color: #f0f8ff;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
            }
            .device-info {
                margin-top: 15px;
                padding: 10px;
                background-color: #e6f2ff;
                border-left: 5px solid #0066cc;
            }
            .disclaimer {
                font-size: 0.8rem;
                font-style: italic;
                margin-top: 30px;
            }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error setting up page configuration: {str(e)}")

def render_sidebar() -> float:
    """
    Render the sidebar with input controls and reference information.

    Returns:
        float: The selected flow rate.
    """
    try:
        with st.sidebar:
            st.header("Input Parameters")
            
            # Flow rate input
            st.subheader("Flow Rate")
            flow_rate = st.slider(
                "Select Flow Rate (LPM)", 
                min_value=MIN_FLOW_RATE, 
                max_value=MAX_FLOW_RATE, 
                value=2.0,
                step=0.5
            )
            
            precise_flow = st.number_input(
                "Or enter exact value (LPM)", 
                min_value=MIN_FLOW_RATE,
                max_value=MAX_FLOW_RATE,
                value=flow_rate,
                step=0.1
            )
            
            try:
                flow_rate = validate_flow_rate(precise_flow if precise_flow != flow_rate else flow_rate)
            except ValueError as e:
                st.error(str(e))
                flow_rate = MIN_FLOW_RATE
            
            st.divider()
            
            # Reference Information
            st.subheader("Quick Reference")
            st.markdown("""
            **Common Devices & Flow Rates:**
            - Nasal Cannula: 1-6 LPM
            - Simple Mask: 5-10 LPM
            - Non-rebreather: 10-15 LPM
            - High Flow Systems: 15+ LPM
            
            **Formula Used:**
            - Room air: 21% O₂
            - Each 1 LPM (nasal cannula) adds ~4% O₂
            """)
        
        return flow_rate
    except Exception as e:
        st.error(f"Error rendering sidebar: {str(e)}")
        return MIN_FLOW_RATE

def main() -> None:
    """Main application entry point."""
    try:
        setup_page_config()
        
        # App Header
        st.markdown("<h1 class='main-header'>Respiratory Therapy Oxygen Calculator</h1>", 
                    unsafe_allow_html=True)
        st.markdown("<p class='subheader'>Convert Flow Rate (LPM) to Approximate O₂ Percentage</p>", 
                    unsafe_allow_html=True)
        
        # Get flow rate from sidebar
        flow_rate = render_sidebar()
        
        # Main content area
        col1, col2 = st.columns([3, 2])
        
        with col1:
            try:
                # Calculate and display results
                o2_percentage, device = calculate_oxygen_percentage(flow_rate)
                
                st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                st.subheader("Results")
                st.markdown(f"### For flow rate of {flow_rate:.1f} LPM:")
                
                # Display gauge chart
                fig = create_gauge_chart(o2_percentage)
                if fig:
                    st.pyplot(fig)
                    plt.close(fig)  # Clean up the figure after displaying
                
                # Device info
                st.markdown(f"<div class='device-info'>", unsafe_allow_html=True)
                st.markdown(f"**Recommended Delivery Device:** {device}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(
                    "<p class='disclaimer'>Note: Actual delivered O₂ percentage may vary based on "
                    "patient factors including respiratory rate, tidal volume, mouth breathing, "
                    "and device fitting.</p>", 
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying results: {str(e)}")
        
        with col2:
            try:
                # Show reference table
                st.subheader("Reference Table")
                df = generate_reference_table()
                if not df.empty:
                    st.table(df)
                
                # Clinical considerations
                st.subheader("Clinical Considerations")
                st.info("""
                **When selecting oxygen flow rates:**
                
                • Consider the patient's baseline SpO₂ and respiratory status
                • Target SpO₂ of 94-98% for most patients
                • For COPD patients, target 88-92% to avoid CO₂ retention
                • Remember that delivery efficiency varies by patient
                """)
            except Exception as e:
                st.error(f"Error displaying reference information: {str(e)}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    finally:
        plt.close('all')  # Ensure all figures are closed

if __name__ == "__main__":
    main()
