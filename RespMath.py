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
    """Main application entry point."""
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
        # Calculate and display results
        o2_percentage, device = calculate_oxygen_percentage(flow_rate)
        
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.subheader("Results")
        st.markdown(f"### For flow rate of {flow_rate:.1f} LPM:")
        
        # Display gauge chart
        fig = create_gauge_chart(o2_percentage)
        st.pyplot(fig)
        
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
    
    with col2:
        # Show reference table
        st.subheader("Reference Table")
        df = generate_reference_table()
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

if __name__ == "__main__":
    main()
