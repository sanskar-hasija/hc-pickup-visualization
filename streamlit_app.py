import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os 
import glob

def process_pickup(pickup):
    pickup['report_date']=pd.to_datetime(pickup['report_date'])
    pickup['stay_date']=pd.to_datetime(pickup['stay_date'])

    rooms_df = pickup[['report_date','stay_date','dynamic_rooms','total_rooms','dynamic_room_revenue','total_room_revenue']]
    return rooms_df


bookings = pd.read_parquet('data/processed_bookings.parquet')
pickup = pd.read_csv('data/pickup.csv')

pickup = process_pickup(pickup)
bookings = bookings.merge(pickup, on=['stay_date', 'report_date'], how='left')

assert (bookings['cumulative_total_bookings'] == bookings['cumulative_total_type_bookings']).sum() == len(bookings)
bookings['booking_diff'] = bookings['cumulative_total_bookings'] - bookings['total_rooms'] 
print( "Percentage of correct mapping in bookings and pickup", ((bookings['cumulative_total_bookings'] == bookings['total_rooms']).sum()/ len(bookings)) * 100)
plot_data = bookings.copy()


min_report_date = plot_data.report_date.min()
max_report_date = plot_data.report_date.max()
new_max_report_date = max_report_date + pd.DateOffset(months=4)
zmin = plot_data.cumulative_total_bookings.min()
zmax = plot_data.cumulative_total_bookings.max()

custom_colorscale = [
    [0, 'white'],         
    [0.2, 'lightblue'],   
    [0.4, 'blue'],        
    [0.6, 'lightgreen'],  
    [0.8, 'yellow'],      
    [1, 'red']            
]
diff_min_val = plot_data['booking_diff'].min()
diff_max_val = plot_data['booking_diff'].max()
diff_mid_val = 0  
zero_position = abs(diff_min_val) / (diff_max_val - diff_min_val)

custom_colorscale_diff = [
    [0, 'blue'],     
    [zero_position / 2, 'lightblue'],        
    [zero_position, 'white'],  
    [zero_position + (1 - zero_position) / 2, '#FFCCCB'],      
    [1, 'red']            
]

trace_individual = go.Heatmap(
    z=plot_data.cumulative_individual_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Individual Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_dynamic_group = go.Heatmap(
    z=plot_data.cumulative_dynamic_group_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Dynamic Group Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_static_group = go.Heatmap(
    z=plot_data.cumulative_static_individual_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Static Individual Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_total = go.Heatmap(
    z=plot_data.cumulative_total_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Total Bookings'),
    zmin=zmin,
    zmax=zmax,
)
trace_pickup = go.Heatmap(
    z=plot_data.total_rooms,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Pickup Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_diff = go.Heatmap(
    z=plot_data.booking_diff,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale_diff,
    colorbar=dict(title='Booking Difference'),
    visible= False
)

fig = go.Figure(data=[trace_individual, trace_dynamic_group, trace_static_group, trace_total, trace_pickup, trace_diff])



buttons = [
    dict(
        label="Individual",
        method="update",
        args=[{"visible": [True, False, False, False, False, False]}],
    ),
    dict(
        label="Dynamic Group",
        method="update",
        args=[{"visible": [False, True, False, False, False, False]}],
    ),
    dict(
        label="Static Individual",
        method="update",
        args=[{"visible": [False, False, True, False, False, False]}],
    ),
    dict(
        label="Total",
        method="update",
        args=[{"visible": [False, False, False, True, False, False]}],
    ),
    dict(
        label="Pickup",
        method="update",
        args=[{"visible": [False, False, False, False, True, False]}],
    ),
    dict(
        label="Booking Difference",
        method="update",
        args=[{"visible": [False, False, False, False, False, True]}],
    )
]


fig.update_layout(
    title=f'Bookings Analysis Segment - 1 , Report Date Range: {min_report_date.date()} - {max_report_date.date()}',
    title_x=0.45,
    updatemenus=[{
        'type': 'dropdown',
        'x': 1.1,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons[:3]
    },
    {
        'type': 'buttons',
        'direction': 'right',
        'x': 0.65,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons[3:]
    }
    ]
)
fig.update_xaxes(title_text="Stay Date")
fig.update_yaxes(title_text="Report Date")

# Show figure
st.plotly_chart(fig)

trace_direct = go.Heatmap(
    z=plot_data.cumulative_direct_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Direct Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)

trace_indirect = go.Heatmap(
    z=plot_data.cumulative_indirect_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Indirect Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)

trace_ota = go.Heatmap(
    z=plot_data.cumulative_ota_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='OTA Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_other_type = go.Heatmap(
    z=plot_data.cumulative_other_type_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Other Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_total = go.Heatmap(
    z=plot_data.cumulative_total_type_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    zmin=zmin,
    zmax=zmax,
    colorbar=dict(title='Total Bookings'),
)
trace_pickup = go.Heatmap(
    z=plot_data.total_rooms,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Pickup Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_diff = go.Heatmap(
    z=plot_data.booking_diff,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale_diff,
    colorbar=dict(title='Booking Difference'),
    visible= False
)


fig = go.Figure(data=[trace_direct, trace_indirect, trace_ota, trace_other_type, trace_total, trace_pickup, trace_diff])



buttons = [
    
    dict(
        label="Direct",
        method="update",
        args=[{"visible": [True, False, False, False, False, False, False]}],
    ),
    dict(
        label="Indirect",
        method="update",
        args=[{"visible": [False, True, False, False, False, False, False]}],
    ),
    dict(
        label="OTA",
        method="update",
        args=[{"visible": [False, False, True, False, False, False, False]}],
    ),
    dict(
        label="Other",
        method="update",
        args=[{"visible": [False, False, False, True, False, False, False]}],
    ),
    dict(
        label="Total",
        method="update",
        args=[{"visible": [False, False, False, False, True, False, False]}],
    ),
    dict(
        label="Pickup",
        method="update",
        args=[{"visible": [False, False, False, False, False, True, False]}],
    ),
    dict(
        label="Booking Difference",
        method="update",
        args=[{"visible": [False, False, False, False, False, False, True]}],
    )
]

fig.update_layout(
    title=f'Bookings Analysis Segment - 2 , Report Date Range: {min_report_date.date()} - {max_report_date.date()}',
    title_x=0.45,
    updatemenus=[{
        'type': 'dropdown',
        'x': 1.1,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons[:4]
    },
    {
        'type': 'buttons',
        'direction': 'right',
        'x': 0.65,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons[4:]
    }
    ]
)
fig.update_xaxes(title_text="Stay Date")
fig.update_yaxes(title_text="Report Date")

# Show figure
st.plotly_chart(fig)


trace_total = go.Heatmap(
    z=plot_data.cumulative_total_type_bookings,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    zmin=zmin,
    zmax=zmax,
    colorbar=dict(title='Total Bookings'),
)
trace_pickup = go.Heatmap(
    z=plot_data.total_rooms,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale,
    colorbar=dict(title='Pickup Bookings'),
    zmin=zmin,
    zmax=zmax,
    visible= False
)
trace_diff = go.Heatmap(
    z=plot_data.booking_diff,
    x=plot_data.stay_date,
    y=plot_data.report_date,
    colorscale=custom_colorscale_diff,
    colorbar=dict(title='Booking Difference'),
    visible= False
)

fig = go.Figure(data=[trace_total, trace_pickup, trace_diff])

buttons = [
    dict(
        label="Total",
        method="update",
        args=[{"visible": [True, False, False]}],
    ),
    dict(
        label="Pickup",
        method="update",
        args=[{"visible": [False, True, False]}],
    ),
    dict(
        label="Booking Difference",
        method="update",
        args=[{"visible": [False, False, True]}],
    )
]
fig.update_layout(
    title=f'Bookings vs Pickup, Report Date Range: {min_report_date.date()} - {max_report_date.date()}',
    title_x=0.45,
    updatemenus=[{
        'type': 'buttons',
        'direction': 'right',
        'x': 0.65,
        'y': 1.15,
        'showactive': True,
        'active': 0,
        'buttons': buttons
    }]
)
fig.update_xaxes(title_text="Stay Date")
fig.update_yaxes(title_text="Report Date")

# Show figure
st.plotly_chart(fig)
