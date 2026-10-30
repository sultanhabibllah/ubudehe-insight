
from pathlib import Path
from html import escape
import textwrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import (
    METRICS,
    NATIONAL,
    load_data,
    compare_provinces,
    calculate_priorities,
    generate_insight,
)

st.set_page_config(
    page_title="Ubudehe Insight",
    page_icon="🇷🇼",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent

css = ROOT / "styles.css"
if css.exists():
    st.markdown(
        f"<style>{css.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

BLACK = "#171717"
CHARCOAL = "#414141"
GREY = "#DCDCD9"
LIGHT = "#F0F0EE"
GRID = "#ECECE9"
WHITE = "#FFFFFF"


@st.cache_data
def get_data():
    return load_data(ROOT / "data" / "poverty_cleaned.csv")


try:
    df = get_data()
except Exception as error:
    st.error(f"Could not load data: {error}")
    st.stop()

provinces = df["province"].tolist()


# =============================================
# REUSABLE UI
# =============================================

def html(content):
    st.markdown(
        textwrap.dedent(content).strip(),
        unsafe_allow_html=True,
    )


def heading(title, description):
    html(f"""
    <div class="page-heading">
        <h1>{escape(title)}</h1>
        <p>{escape(description)}</p>
    </div>
    """)


def section(title, description=""):
    html(f"""
    <div class="section-heading">
        <h2>{escape(title)}</h2>
        <p>{escape(description)}</p>
    </div>
    """)


def kpi(label, value, detail):
    html(f"""
    <div class="kpi-card">
        <div class="kpi-label">{escape(str(label))}</div>
        <div class="kpi-value">{escape(str(value))}</div>
        <div class="kpi-detail">{escape(str(detail))}</div>
    </div>
    """)


def panel(title, description):
    html(f"""
    <div class="info-panel">
        <div class="info-title">{escape(title)}</div>
        <p>{escape(description)}</p>
    </div>
    """)


def featured(label, value, description):
    html(f"""
    <div class="featured-panel">
        <div class="featured-label">{escape(label)}</div>
        <div class="featured-value">{escape(str(value))}</div>
        <p>{escape(description)}</p>
    </div>
    """)


def gap():
    st.write("")


def data_table(frame, percentage_columns=None, decimals=None):
    """White, custom HTML table for small official datasets."""
    percentage_columns = percentage_columns or []
    decimals = decimals or {}

    head = "".join(
        f"<th scope='col'>{escape(str(c))}</th>"
        for c in frame.columns
    )

    rows = []
    for _, row in frame.iterrows():
        cells = []
        for col, value in row.items():
            if pd.isna(value):
                shown = "—"
            elif isinstance(value, (int, float)):
                precision = decimals.get(col, 1)
                shown = f"{value:,.{precision}f}"
                if col in percentage_columns:
                    shown += "%"
            else:
                shown = str(value)
            cells.append(f"<td>{escape(shown)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    html(
        '<div class="table-scroll"><table class="data-table">'
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def chart_style(fig, height=360, legend=False):
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Arial, sans-serif",
            color=BLACK,
            size=13,
        ),
        showlegend=legend,
        margin=dict(l=12, r=44, t=30, b=30),
        bargap=0.32,
        hoverlabel=dict(
            bgcolor=WHITE,
            font=dict(color=BLACK),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        showline=False,
        tickfont=dict(color=CHARCOAL, size=12),
        title_font=dict(color=CHARCOAL),
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont=dict(color=BLACK, size=13),
        title_font=dict(color=CHARCOAL),
    )
    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def province_chart(column, selected=None, national=None):
    ordered = df.sort_values(column)

    colors = [
        BLACK if p == selected else GREY
        for p in ordered["province"]
    ]

    fig = go.Figure(go.Bar(
        x=ordered[column],
        y=ordered["province"],
        orientation="h",
        marker_color=colors,
        text=[f"{x:.1f}%" for x in ordered[column]],
        textposition="outside",
        textfont=dict(size=14, color=BLACK),
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))

    if national is not None:
        fig.add_vline(
            x=national,
            line_dash="dot",
            line_color=CHARCOAL,
            line_width=1.3,
        )
        fig.add_annotation(
            x=national,
            y=1.09,
            yref="paper",
            text="National average",
            showarrow=False,
            font=dict(size=12, color=CHARCOAL),
        )

    fig.update_xaxes(
        title=None,
        ticksuffix="%",
        range=[0, max(46, df[column].max() + 7)],
    )
    fig.update_yaxes(title=None)
    return chart_style(fig, 370)


def comparison_chart(comp):
    metrics = [
        ("Monetary poverty", "monetary_poverty"),
        ("Multidimensional poverty", "mpi_incidence"),
    ]

    fig = go.Figure()

    for i, (_, row) in enumerate(comp.iterrows()):
        values = [float(row[col]) for _, col in metrics]
        fig.add_trace(go.Bar(
            name=row["province"],
            x=[label for label, _ in metrics],
            y=values,
            marker_color=BLACK if i == 0 else GREY,
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
            textfont=dict(size=14, color=BLACK),
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        legend=dict(
            orientation="h",
            y=1.17,
            x=0,
            bgcolor=WHITE,
            font=dict(size=13, color=BLACK),
        ),
    )
    fig.update_yaxes(range=[0, 50], title=None)
    fig.update_xaxes(title=None, showgrid=False)
    return chart_style(fig, 380, legend=True)


def ranking_chart(ranked):
    ordered = ranked.sort_values("priority_score")
    first = ranked.iloc[0]["province"]

    fig = go.Figure(go.Bar(
        x=ordered["priority_score"],
        y=ordered["province"],
        orientation="h",
        marker_color=[
            BLACK if p == first else GREY
            for p in ordered["province"]
        ],
        text=[f"{x:.1f}" for x in ordered["priority_score"]],
        textposition="outside",
        textfont=dict(size=14, color=BLACK),
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.1f}<extra></extra>",
    ))
    fig.update_xaxes(range=[0, 110], title=None)
    fig.update_yaxes(title=None)
    return chart_style(fig, 370)


def confidence_chart():
    fig = go.Figure(go.Scatter(
        x=df["province"],
        y=df["monetary_poverty"],
        mode="markers",
        marker=dict(color=BLACK, size=11),
        error_y=dict(
            type="data",
            symmetric=False,
            array=df["monetary_ci_upper"] - df["monetary_poverty"],
            arrayminus=df["monetary_poverty"] - df["monetary_ci_lower"],
            color=CHARCOAL,
            thickness=1.6,
            width=6,
            visible=True,
        ),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    fig.update_yaxes(title="Poverty rate (%)", range=[0, 45])
    return chart_style(fig, 350)


def brief(province, row):
    return f"""UBUDEHE INSIGHT
Regional Poverty Evidence Brief

Province: {province}
NISR EICV7 (2023/24)

Monetary poverty: {row['monetary_poverty']:.1f}%
National estimate: {NATIONAL['monetary_poverty']:.1f}%
Confidence interval: {row['monetary_ci_lower']:.1f}%–{row['monetary_ci_upper']:.1f}%

Multidimensional poverty incidence: {row['mpi_incidence']:.1f}%
Multidimensional poverty intensity: {row['mpi_intensity']:.1f}%
MPI index: {row['mpi_index']:.3f}

Interpretation:
{generate_insight(df, province)}

Sources:
EICV7 Poverty Profile, Table 0.1
EICV7 Multidimensional Poverty, Table B.5

These are provincial aggregate estimates, not predictions
or causal evaluations of interventions.
"""



# =============================================
# SIDEBAR NAVIGATION
# =============================================

PAGES = [
    ("Overview", "overview", "dashboard"),
    ("Poverty Explorer", "explorer", "bar_chart"),
    ("Regional Comparison", "comparison", "compare_arrows"),
    ("Scenario Lab", "scenario", "tune"),
    ("Evidence & Data", "evidence", "database"),
]

if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"


def navigate(destination):
    st.session_state.current_page = destination


with st.sidebar:
    html("""
    <div class="brand">
        <div class="brand-mark">U</div>
        <div>
            <div class="brand-name">Ubudehe Insight</div>
            <div class="brand-subtitle">Rwanda Poverty Intelligence</div>
        </div>
    </div>
    """)

    st.markdown("**Main menu**")

    for label, page_id, icon_name in PAGES:
        active = st.session_state.current_page == page_id

        with st.container(key=f"nav_{page_id}"):
            st.button(
                label,
                icon=f":material/{icon_name}:",
                key=f"button_{page_id}",
                type="primary" if active else "secondary",
                use_container_width=True,
                on_click=navigate,
                args=(page_id,),
            )

    st.divider()

    st.markdown("**Data source**")
    st.write("NISR EICV7 · 2023/24")
    st.write("Five provinces of Rwanda")

    st.divider()

    st.markdown("**Competition**")
    st.write("NISR Big Data Hackathon 2026")


# =============================================
# MAIN CONTENT
# =============================================

page = st.session_state.current_page

# OVERVIEW

if page == "overview":
    heading(
        "Poverty overview",
        "A national view of Rwanda's poverty patterns, "
        "using official EICV7 household survey statistics.",
    )

    a, b, c = st.columns(3, gap="medium")

    with a:
        kpi(
            "National monetary poverty",
            f"{NATIONAL['monetary_poverty']:.1f}%",
            "Population below the monetary poverty line",
        )
    with b:
        kpi(
            "Multidimensional poverty",
            f"{NATIONAL['mpi_incidence']:.1f}%",
            "National multidimensional poverty incidence",
        )
    with c:
        top = df.loc[df["monetary_poverty"].idxmax()]
        kpi(
            "Highest provincial rate",
            f"{top['monetary_poverty']:.1f}%",
            top["province"],
        )

    gap()
    left, right = st.columns([1.8, 1], gap="large")

    with left:
        section(
            "Monetary poverty by province",
            "Provincial estimates, with the highest rate highlighted.",
        )
        show_chart(province_chart(
            "monetary_poverty",
            selected=top["province"],
            national=NATIONAL["monetary_poverty"],
        ))

    with right:
        featured(
            "Highest monetary poverty",
            f"{top['monetary_poverty']:.1f}%",
            top["province"],
        )

        gap()
        low = df.loc[df["monetary_poverty"].idxmin()]
        kpi(
            "Lowest provincial rate",
            f"{low['monetary_poverty']:.1f}%",
            low["province"],
        )

        gap()
        max_mpi = df.loc[df["mpi_incidence"].idxmax()]
        kpi(
            "Highest MPI incidence",
            f"{max_mpi['mpi_incidence']:.1f}%",
            max_mpi["province"],
        )

    gap()
    section("Key finding")
    panel(
        "Different measures reveal different regional patterns",
        "The province with the highest monetary poverty "
        "is not necessarily the province with the highest "
        "multidimensional poverty incidence. Comparing "
        "both indicators helps identify different dimensions "
        "of deprivation.",
    )


# POVERTY EXPLORER

elif page == "explorer":
    heading(
        "Poverty explorer",
        "Investigate provincial indicators and see how "
        "they compare with national estimates.",
    )

    a, b = st.columns(2)
    with a:
        province = st.selectbox(
            "Province",
            provinces,
            index=provinces.index("Western"),
        )
    with b:
        metric_name = st.selectbox(
            "Indicator",
            list(METRICS.keys()),
        )

    row = df.loc[df["province"] == province].iloc[0]

    a, b, c = st.columns(3)
    with a:
        kpi(
            "Monetary poverty",
            f"{row['monetary_poverty']:.1f}%",
            f"{row['monetary_poverty']-NATIONAL['monetary_poverty']:+.1f} percentage points vs national",
        )
    with b:
        kpi(
            "Multidimensional poverty",
            f"{row['mpi_incidence']:.1f}%",
            f"{row['mpi_incidence']-NATIONAL['mpi_incidence']:+.1f} percentage points vs national",
        )
    with c:
        kpi("MPI index", f"{row['mpi_index']:.3f}", province)

    gap()
    section(
        f"{metric_name} by province",
        "The selected province is highlighted in black.",
    )

    show_chart(province_chart(
        METRICS[metric_name],
        selected=province,
        national=NATIONAL[METRICS[metric_name]],
    ))

    gap()
    panel(
        f"About {province}",
        generate_insight(df, province),
    )

    gap()
    st.download_button(
        "Download evidence brief",
        data=brief(province, row),
        file_name=f"ubudehe_{province.lower().replace(' ', '_')}.txt",
        mime="text/plain",
    )


# REGIONAL COMPARISON

elif page == "comparison":
    heading(
        "Regional comparison",
        "Compare two provinces across monetary and "
        "multidimensional poverty indicators.",
    )

    a, b = st.columns(2)
    with a:
        first = st.selectbox(
            "First province",
            provinces,
            index=provinces.index("Western"),
        )
    with b:
        second = st.selectbox(
            "Second province",
            provinces,
            index=provinces.index("Southern"),
        )

    if first == second:
        st.warning("Choose two different provinces.")
    else:
        comp = compare_provinces(df, first, second)

        monetary_gap = abs(
            comp.iloc[0]["monetary_poverty"]
            - comp.iloc[1]["monetary_poverty"]
        )
        mpi_gap = abs(
            comp.iloc[0]["mpi_incidence"]
            - comp.iloc[1]["mpi_incidence"]
        )

        a, b = st.columns(2)
        with a:
            kpi(
                "Monetary poverty difference",
                f"{monetary_gap:.1f} pp",
                f"{first} compared with {second}",
            )
        with b:
            kpi(
                "MPI incidence difference",
                f"{mpi_gap:.1f} pp",
                f"{first} compared with {second}",
            )

        gap()
        section(
            "Comparing poverty indicators",
            "Black and grey bars distinguish the two provinces.",
        )
        show_chart(comparison_chart(comp))

        gap()
        section("Detailed figures")
        display = comp[
            [
                "province",
                "monetary_poverty",
                "mpi_incidence",
                "mpi_intensity",
                "mpi_index",
            ]
        ].rename(columns={
            "province": "Province",
            "monetary_poverty": "Monetary poverty",
            "mpi_incidence": "MPI incidence",
            "mpi_intensity": "MPI intensity",
            "mpi_index": "MPI index",
        })

        data_table(
            display,
            percentage_columns=[
                "Monetary poverty",
                "MPI incidence",
                "MPI intensity",
            ],
            decimals={"MPI index": 3},
        )

        gap()
        panel(
            "Comparative finding",
            f"The provinces differ by {monetary_gap:.1f} "
            f"percentage points in monetary poverty and "
            f"{mpi_gap:.1f} percentage points in MPI incidence. "
            "These descriptive differences have not been "
            "tested for statistical significance.",
        )

        st.download_button(
            "Download comparison",
            comp.to_csv(index=False),
            file_name="ubudehe_comparison.csv",
            mime="text/csv",
        )


# SCENARIO LAB

elif page == "scenario":
    heading(
        "Scenario lab",
        "Explore how changing indicator weights affects "
        "illustrative regional priority rankings.",
    )

    a, b = st.columns(2)
    with a:
        monetary_weight = st.slider(
            "Monetary poverty weight",
            0, 100, 50, 5,
        )
    with b:
        mpi_weight = st.slider(
            "Multidimensional poverty weight",
            0, 100, 50, 5,
        )

    total = monetary_weight + mpi_weight

    if total == 0:
        st.warning("At least one weight must be above zero.")
    else:
        ranked = calculate_priorities(df, {
            "monetary_poverty": monetary_weight,
            "mpi_incidence": mpi_weight,
        })

        leader = ranked.iloc[0]

        a, b, c = st.columns(3)
        with a:
            kpi(
                "Monetary weighting",
                f"{monetary_weight/total:.0%}",
                "Effective weight",
            )
        with b:
            kpi(
                "Multidimensional weighting",
                f"{mpi_weight/total:.0%}",
                "Effective weight",
            )
        with c:
            kpi(
                "Top priority score",
                f"{leader['priority_score']:.1f}",
                leader["province"],
            )

        gap()
        section(
            "Relative regional ranking",
            "The top-ranked province is highlighted.",
        )
        show_chart(ranking_chart(ranked))

        gap()
        featured(
            "Highest relative priority",
            leader["province"],
            f"Score of {leader['priority_score']:.1f} out of 100 "
            "under the selected assumptions.",
        )

        gap()
        section("All scenario results")
        display = ranked.rename(columns={
            "province": "Province",
            "priority_score": "Priority score",
        })
        data_table(display)

        st.download_button(
            "Download scenario",
            ranked.to_csv(index=False),
            file_name="ubudehe_scenario.csv",
            mime="text/csv",
        )

        with st.expander("Methodology and limitations"):
            st.write(
                "Indicators are min-max normalized across five "
                "provinces and combined using normalized weights. "
                "The resulting ranking is illustrative, not an "
                "estimate of funding requirements, causal impact "
                "or intervention effectiveness. Population sizes "
                "and sampling uncertainty are not incorporated."
            )


# EVIDENCE & DATA

elif page == "evidence":
    heading(
        "Evidence & data",
        "Review the official survey indicators, "
        "statistical uncertainty and methodology.",
    )

    a, b, c = st.columns(3)
    with a:
        kpi("Province records", len(df), "Five provinces")
    with b:
        kpi(
            "Missing values",
            int(df.isna().sum().sum()),
            "Validated cleaned extract",
        )
    with c:
        kpi(
            "Duplicate records",
            int(df["province"].duplicated().sum()),
            "Unique province names",
        )

    gap()
    section(
        "Provincial dataset",
        "Cleaned data extracted from NISR EICV7 tables.",
    )

    display = df.rename(columns={
        "province": "Province",
        "monetary_poverty": "Monetary poverty",
        "monetary_ci_lower": "CI lower",
        "monetary_ci_upper": "CI upper",
        "mpi_incidence": "MPI incidence",
        "mpi_intensity": "MPI intensity",
        "mpi_index": "MPI index",
    })

    data_table(
        display,
        percentage_columns=[
            "Monetary poverty",
            "CI lower",
            "CI upper",
            "MPI incidence",
            "MPI intensity",
        ],
        decimals={"MPI index": 3},
    )

    st.download_button(
        "Download cleaned data",
        df.to_csv(index=False),
        file_name="ubudehe_cleaned.csv",
        mime="text/csv",
    )

    gap()
    section(
        "Statistical uncertainty",
        "Published monetary poverty confidence intervals.",
    )
    show_chart(confidence_chart())

    gap()
    section("Indicator definitions")

    dictionary = pd.DataFrame([
        {
            "Indicator": "Monetary poverty",
            "Definition": "Share below the monetary poverty line",
        },
        {
            "Indicator": "MPI incidence",
            "Definition": "Share identified as multidimensionally poor",
        },
        {
            "Indicator": "MPI intensity",
            "Definition": "Average deprivation among MPI-poor people",
        },
        {
            "Indicator": "MPI index",
            "Definition": "Incidence multiplied by intensity",
        },
    ])
    data_table(dictionary)

    gap()
    section("Original data sources")

    st.markdown(
        "[NISR EICV7 Poverty Profile]"
        "(https://statistics.gov.rw/data-sources/surveys/EICV/"
        "integrated-household-living-conditions-survey-7-eicv-7/"
        "eicv7-poverty-profile-report-202324)"
    )
    st.markdown(
        "[NISR EICV7 Multidimensional Poverty]"
        "(https://statistics.gov.rw/data-sources/surveys/EICV/"
        "integrated-household-living-conditions-survey-7-eicv-7/"
        "eicv7-thematic-report-multidimensional-poverty)"
    )

    panel(
        "Methodological limitation",
        "This application works with provincial survey "
        "aggregates. It does not identify individual "
        "households, establish causal effects or predict "
        "intervention success.",
    )


st.divider()
st.caption(
    "Ubudehe Insight · NISR Big Data Hackathon 2026 · "
    "EICV7 (2023/24)"
)
