import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import io  # Add this line
from datetime import date
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Law Firm Partner KPI Tracker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e89ae;
        color: white;
    }
    .category-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin-bottom: 1rem;
    }
    .metric-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .status-completed {
        color: green;
        font-weight: bold;
    }
    .status-in-progress {
        color: orange;
        font-weight: bold;
    }
    .status-planned {
        color: blue;
        font-weight: bold;
    }
    .status-attention {
        color: red;
        font-weight: bold;
    }
    .reminder-box {
        background-color: #fffde7;
        padding: 1rem;
        border-left: 4px solid #ffd54f;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data
if 'kpi_data' not in st.session_state:
    # Check if the CSV file exists
    if os.path.exists('kpi_data.csv'):
        st.session_state.kpi_data = pd.read_csv('kpi_data.csv')
    else:
        # Initialize with empty dataframe
        st.session_state.kpi_data = pd.DataFrame(columns=[
            'partner', 'category', 'metric_id', 'metric_name', 'status',
            'value_text', 'value_number', 'date_value', 'last_updated'
        ])

# Define partners
partners = ["Gints", "Debora", "Jūlija", "Brigita", "Jānis", "Reinis", "Ineta"]

# Define KPI categories and metrics
kpi_structure = {
    "Finanšu mērķi": [
        {"id": "fin_1", "name": "Reģistrētās stundas", "type": "number", "description": "Advokāts nodrošina vismaz XY reģistrētas stundas mēnesī"},
        {"id": "fin_2", "name": "Prakses grupas apgrozījums", "type": "number"},
        {"id": "fin_3", "name": "Peļņas rādītājs", "type": "number"},
        {"id": "fin_4", "name": "Esošo klientu jauni uzdevumi", "type": "text"},
        {"id": "fin_5", "name": "Klientu apgrozījuma pieaugums", "type": "number"}
    ],
    "Publicitāte & Marketings": [
        {"id": "pub_1", "name": "Publikācijas", "type": "text", "description": "Minimums 3x gadā"},
        {"id": "pub_2", "name": "Weblapas aktualizācija", "type": "text"},
        {"id": "pub_3", "name": "Publiskas uzstāšanās", "type": "text"},
        {"id": "pub_4", "name": "Intervijas medijos", "type": "text"},
        {"id": "pub_5", "name": "Legal500 un Chambers reitingi", "type": "text"},
        {"id": "pub_6", "name": "Pro bono aktivitātes", "type": "text"},
        {"id": "pub_7", "name": "Konferenču apmeklēšana", "type": "text"}
    ],
    "Klientu tieša piesaiste": [
        {"id": "client_1", "name": "Jaunu klientu piesaiste", "type": "text"},
        {"id": "client_2", "name": "Piesaistes iniciatīvas", "type": "text"},
        {"id": "client_3", "name": "Tikšanās ar klientiem", "type": "text"},
        {"id": "client_4", "name": "Road shows", "type": "text"},
        {"id": "client_5", "name": "Piedāvājumu gatavošana", "type": "text"}
    ],
    "Darba kvalitāte": [
        {"id": "qual_1", "name": "Klientu atsauksmes", "type": "text"},
        {"id": "qual_2", "name": "Konsultācijas ar kolēģiem", "type": "text"},
        {"id": "qual_3", "name": "Profesionālā attīstība", "type": "text"}
    ],
    "Pro Bono Aktivitātes": [
        {"id": "probono_1", "name": "Pro Bono Projekti", "type": "text"},
        {"id": "probono_2", "name": "Mentoring & Education", "type": "text"}
    ],
    "Biroja pārstāvēšana tīklos": [
        {"id": "network_1", "name": "IFG & SCG Aktivitātes", "type": "text"},
        {"id": "network_2", "name": "Starptautiskā sadarbība", "type": "text"}
    ],
    "Līdzdalība Biroja ikdienā": [
        {"id": "daily_1", "name": "Kolēģu apmācība un attīstība", "type": "text"},
        {"id": "daily_2", "name": "Biroja pasākumu organizēšana", "type": "text"},
        {"id": "daily_3", "name": "Administratīvie pienākumi", "type": "text"},
        {"id": "daily_4", "name": "Īpašās iemaņas & ieguldījums", "type": "text"}
    ]
}

# Status options
status_options = [
    "Not Started", 
    "In Progress", 
    "Completed", 
    "Needs Attention"
]

def save_data():
    """Save the current KPI data to a CSV file"""
    st.session_state.kpi_data.to_csv('kpi_data.csv', index=False)
    st.success("Data saved successfully!")

def add_or_update_kpi(partner, category, metric_id, metric_name, status, value_text=None, value_number=None, date_value=None):
    """Add or update a KPI entry"""
    # Check if entry exists
    mask = (
        (st.session_state.kpi_data['partner'] == partner) & 
        (st.session_state.kpi_data['metric_id'] == metric_id)
    )
    
    if mask.any():
        # Update existing entry
        idx = st.session_state.kpi_data[mask].index[0]
        st.session_state.kpi_data.at[idx, 'status'] = status
        if value_text is not None:
            st.session_state.kpi_data.at[idx, 'value_text'] = value_text
        if value_number is not None:
            st.session_state.kpi_data.at[idx, 'value_number'] = value_number
        if date_value is not None:
            st.session_state.kpi_data.at[idx, 'date_value'] = date_value
        st.session_state.kpi_data.at[idx, 'last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Add new entry
        new_entry = {
            'partner': partner,
            'category': category,
            'metric_id': metric_id,
            'metric_name': metric_name,
            'status': status,
            'value_text': value_text if value_text is not None else "",
            'value_number': value_number if value_number is not None else np.nan,
            'date_value': date_value if date_value is not None else "",
            'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.kpi_data = pd.concat([st.session_state.kpi_data, pd.DataFrame([new_entry])], ignore_index=True)

def get_kpi_value(partner, metric_id, value_type='text'):
    """Get the current value of a KPI for a partner"""
    mask = (
        (st.session_state.kpi_data['partner'] == partner) & 
        (st.session_state.kpi_data['metric_id'] == metric_id)
    )
    
    if mask.any():
        if value_type == 'text':
            return st.session_state.kpi_data[mask]['value_text'].iloc[0]
        elif value_type == 'number':
            return st.session_state.kpi_data[mask]['value_number'].iloc[0]
        elif value_type == 'date':
            return st.session_state.kpi_data[mask]['date_value'].iloc[0]
        elif value_type == 'status':
            return st.session_state.kpi_data[mask]['status'].iloc[0]
    
    # Return default values if not found
    if value_type == 'text':
        return ""
    elif value_type == 'number':
        return None
    elif value_type == 'date':
        return None
    elif value_type == 'status':
        return status_options[0]

def render_status_badge(status):
    """Render a formatted status badge"""
    if status == "Completed":
        return f'<span class="status-completed">● {status}</span>'
    elif status == "In Progress":
        return f'<span class="status-in-progress">● {status}</span>'
    elif status == "Not Started":
        return f'<span class="status-planned">● {status}</span>'
    elif status == "Needs Attention":
        return f'<span class="status-attention">● {status}</span>'
    return status

def main():
    st.title("⚖️ Law Firm Partner KPI Tracker")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigate")
        # Reporting period selector
        today = date.today()
        month = st.selectbox("Reporting Month", options=range(1, 13), index=today.month-1, format_func=lambda x: datetime.date(2024, x, 1).strftime('%B'))
        year = st.selectbox("Reporting Year", options=range(2023, 2026), index=1)
        
        app_mode = st.radio("Mode", ["Input KPIs", "View Reports"])
        
        if st.button("Save Data"):
            save_data()
            
        st.markdown("---")
        st.markdown("### Quick Links")
        st.markdown("- [KPI Documentation](https://example.com)")
        st.markdown("- [Help Guide](https://example.com)")
        
        st.markdown("---")
        st.info("Last data update: " + 
                (st.session_state.kpi_data['last_updated'].max() 
                 if not st.session_state.kpi_data.empty and 'last_updated' in st.session_state.kpi_data.columns 
                 else "No data yet"))
                
    if app_mode == "Input KPIs":
        # Partner selector
        selected_partner = st.selectbox("Select Partner", partners)
        
        # Create tabs for each category
        tabs = st.tabs([category for category in kpi_structure.keys()])
        
        # Process each category tab
        for i, (category, metrics) in enumerate(kpi_structure.items()):
            with tabs[i]:
                for metric in metrics:
                    with st.expander(f"{metric['name']}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            if "description" in metric:
                                st.markdown(f"*{metric['description']}*")
                        
                        with col2:
                            current_status = get_kpi_value(selected_partner, metric['id'], 'status')
                            status = st.selectbox("Status", 
                                               options=status_options,
                                               index=status_options.index(current_status) if current_status in status_options else 0,
                                               key=f"status_{metric['id']}")
                        
                        if metric['type'] == 'text':
                            text_value = st.text_area("Details", 
                                                   value=get_kpi_value(selected_partner, metric['id'], 'text'),
                                                   height=100,
                                                   key=f"text_{metric['id']}")
                            
                            add_or_update_kpi(
                                selected_partner, 
                                category, 
                                metric['id'], 
                                metric['name'], 
                                status, 
                                value_text=text_value
                            )
                            
                        elif metric['type'] == 'number':
                            current_value = get_kpi_value(selected_partner, metric['id'], 'number')
                            number_value = st.number_input("Value", 
                                                        value=float(current_value) if pd.notna(current_value) else 0.0,
                                                        key=f"number_{metric['id']}")
                            
                            add_or_update_kpi(
                                selected_partner, 
                                category, 
                                metric['id'], 
                                metric['name'], 
                                status, 
                                value_number=number_value
                            )
        
        st.markdown("---")
        st.markdown('<div class="reminder-box">Remember to click "Save Data" in the sidebar when you\'re done updating your KPIs!</div>', unsafe_allow_html=True)
        
    else:  # Reports mode
        st.header("KPI Reports & Analytics")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            report_partner = st.selectbox("Partner", ["All Partners"] + partners)
        with col2:
            report_category = st.selectbox("Category", ["All Categories"] + list(kpi_structure.keys()))
        with col3:
            report_status = st.selectbox("Status", ["All Statuses"] + status_options)
            
        # Apply filters
        filtered_data = st.session_state.kpi_data.copy()
        
        if report_partner != "All Partners":
            filtered_data = filtered_data[filtered_data['partner'] == report_partner]
            
        if report_category != "All Categories":
            filtered_data = filtered_data[filtered_data['category'] == report_category]
            
        if report_status != "All Statuses":
            filtered_data = filtered_data[filtered_data['status'] == report_status]
            
        # Show data table
        if not filtered_data.empty:
            st.subheader("KPI Data")
            st.dataframe(
                filtered_data[['partner', 'category', 'metric_name', 'status', 'value_text', 'value_number', 'last_updated']]
                .rename(columns={
                    'partner': 'Partner',
                    'category': 'Category',
                    'metric_name': 'Metric',
                    'status': 'Status',
                    'value_text': 'Details',
                    'value_number': 'Value',
                    'last_updated': 'Last Updated'
                }),
                hide_index=True
            )
            
            # Status Distribution
            st.subheader("KPI Status Distribution")
            
            if report_partner != "All Partners":
                # Single partner view
                status_counts = filtered_data['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                fig = px.pie(status_counts, values='Count', names='Status', 
                            color='Status',
                            color_discrete_map={
                                'Completed': 'green',
                                'In Progress': 'orange',
                                'Not Started': 'blue',
                                'Needs Attention': 'red'
                            })
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Multiple partners view
                status_by_partner = pd.crosstab(filtered_data['partner'], filtered_data['status'])
                
                # Fill missing statuses with 0
                for status in status_options:
                    if status not in status_by_partner.columns:
                        status_by_partner[status] = 0
                
                fig = px.bar(status_by_partner.reset_index().melt(id_vars='partner', var_name='status', value_name='count'),
                            x='partner', y='count', color='status', barmode='stack',
                            labels={'partner': 'Partner', 'count': 'Count', 'status': 'Status'},
                            color_discrete_map={
                                'Completed': 'green',
                                'In Progress': 'orange',
                                'Not Started': 'blue',
                                'Needs Attention': 'red'
                            })
                st.plotly_chart(fig, use_container_width=True)
            
            # Export button
           if st.button("Export to Excel"):
    try:
        # Create a BytesIO object
        buffer = io.BytesIO()
        
        # Write DataFrame to Excel
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            filtered_data[['partner', 'category', 'metric_name', 'status', 'value_text', 'value_number', 'last_updated']].to_excel(writer, sheet_name='KPI_Report', index=False)
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['KPI_Report']
            
            # Add some formatting
            header_format = workbook.add_format({'bold': True, 'bg_color': '#4e89ae', 'color': 'white'})
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(filtered_data[['partner', 'category', 'metric_name', 'status', 'value_text', 'value_number', 'last_updated']].columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Adjust column widths
            worksheet.set_column('A:B', 15)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 20)
        
        # Download button
        st.download_button(
            label="Download Excel file",
            data=buffer.getvalue(),
            file_name="kpi_report.xlsx",
            mime="application/vnd.ms-excel"
        )
        
    except Exception as e:
        st.error(f"Error generating Excel file: {e}")
        st.info("Make sure you have the required packages installed: openpyxl and xlsxwriter")

if __name__ == "__main__":
    main()
