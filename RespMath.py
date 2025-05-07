import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_oxygen_percentage(flow_rate_lpm):
    """
    Calculate approximate oxygen percentage based on flow rate in liters per minute (LPM).
    
    For nasal cannula and simple masks:
    - Each 1 LPM adds approximately 4% oxygen above room air (21%)
    - Valid for flow rates typically between 1-15 LPM
    
    Returns a tuple of (estimated_percentage, device_recommendation)
    """
    if flow_rate_lpm <= 0:
        return 21, "No supplemental oxygen (room air)"
    
    # Base calculation for low to moderate flow rates
    if flow_rate_lpm <= 6:
        # For nasal cannula: each 1 LPM adds ~4% O2 above room air
        estimated_percentage = 21 + (flow_rate_lpm * 4)
        device = "Nasal Cannula"
    elif flow_rate_lpm <= 10:
        # For simple mask: higher concentration but diminishing returns
        estimated_percentage = 40 + ((flow_rate_lpm - 5) * 4)
        device = "Simple Mask"
    elif flow_rate_lpm <= 15:
        # For non-rebreather or partial rebreather masks
        estimated_percentage = 60 + ((flow_rate_lpm - 10) * 3)
        device = "Non-rebreather/Partial Rebreather Mask"
    else:
        # High flow systems
        estimated_percentage = 90
        device = "High Flow System or Venturi Mask (exact % depends on specific setup)"
    
    # Cap the maximum at 100%
    estimated_percentage = min(estimated_percentage, 100)
    
    return estimated_percentage, device

def main():
    st.set_page_config(
        page_title="RT Oxygen Calculator",
        page_icon="🫁",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
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
    
    # App Header
    st.markdown("<h1 class='main-header'>Respiratory Therapy Oxygen Calculator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subheader'>Convert Flow Rate (LPM) to Approximate O₂ Percentage</p>", unsafe_allow_html=True)
    
    # Create sidebar for input controls
    with st.sidebar:
        st.header("Input Parameters")
        
        # Flow rate input with slider and number input
        st.subheader("Flow Rate")
        flow_rate = st.slider("Select Flow Rate (LPM)", 
                              min_value=0.0, 
                              max_value=20.0, 
                              value=2.0,
                              step=0.5)
        
        # Alternative precise input
        precise_flow = st.number_input("Or enter exact value (LPM)", 
                                       min_value=0.0,
                                       max_value=50.0,
                                       value=flow_rate,
                                       step=0.1)
        
        # Use the precise flow if it differs from slider
        if precise_flow != flow_rate:
            flow_rate = precise_flow
        
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
    
    # Main content area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Calculate the oxygen percentage
        o2_percentage, device = calculate_oxygen_percentage(flow_rate)
        
        # Display results
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        
        st.subheader("Results")
        st.markdown(f"### For flow rate of {flow_rate:.1f} LPM:")
        
        # Use gauge chart for visual representation
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Create gauge chart
        gauge_range = np.linspace(0, 100, 100)
        ax.barh([0], [100], color='lightgray', height=0.5)
        ax.barh([0], [o2_percentage], color='#0066cc', height=0.5)
        
        # Setting y-axis properties
        ax.set_yticks([])
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 21, 40, 60, 80, 100])
        ax.set_xticklabels(['0%', '21%\n(Room Air)', '40%', '60%', '80%', '100%'])
        
        # Add the actual percentage as text
        ax.text(o2_percentage, 0, f"{o2_percentage:.1f}%", 
                ha='center', va='center', fontsize=14, 
                fontweight='bold', color='white',
                bbox=dict(facecolor='#0066cc', alpha=0.8, boxstyle='round,pad=0.5'))
        
        ax.set_title(f"Approximate O₂ Percentage", fontsize=14)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Device info
        st.markdown(f"<div class='device-info'>", unsafe_allow_html=True)
        st.markdown(f"**Recommended Delivery Device:** {device}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<p class='disclaimer'>Note: Actual delivered O₂ percentage may vary based on patient factors including respiratory rate, tidal volume, mouth breathing, and device fitting.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Show a table of common values
        st.subheader("Reference Table")
        
        # Generate data for the table
        flow_values = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15]
        table_data = []
        
        for flow in flow_values:
            percentage, dev = calculate_oxygen_percentage(flow)
            table_data.append({
                "Flow Rate (LPM)": flow,
                "O₂ %": f"{percentage:.1f}%",
                "Device": dev.split(" (")[0]  # Simplify device name for table
            })
        
        df = pd.DataFrame(table_data)
        st.table(df)
        
        # Educational information
        st.subheader("Clinical Considerations")
        st.info("""
        **When selecting oxygen flow rates:**
        
        • Consider the patient's baseline SpO₂ and respiratory status
        • Target SpO₂ of 94-98% for most patients
        • For COPD patients, target 88-92% to avoid CO₂ retention
        • Remember that delivery efficiency varies by patient
        """)

if __name__ == "__main__":
    main()