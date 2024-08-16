import pandas as pd
import plotly.express as px
import streamlit as st


class VisualizationBuilder:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the VisualizationBuilder with the data.

        :param data: The DataFrame containing the data to visualize.
        """
        self.data = data

        # Define a mapping between chart types and Plotly functions
        self.chart_functions = {
            # Basics
            "scatter": self.create_scatter_chart,
            "line": self.create_line_chart,
            "area": self.create_area_chart,
            "bar": self.create_bar_chart,
            "funnel": self.create_funnel_chart,
            "timeline": self.create_timeline_chart,
            # Part-of-Whole
            "pie": self.create_pie_chart,
            "sunburst": self.create_sunburst,
            "treemap": self.create_treemap,
            "icicle": self.create_icicle_chart,
            "funnel_area": self.create_funnel_area_chart,
            # 1D Distributions
            "histogram": self.create_histogram_chart,
            "box": self.create_box_plot,
            "violin": self.create_violin_plot,
            "strip": self.create_strip_plot,
            "ecdf": self.create_ecdf_plot,
            # 2D Distributions
            "density_heatmap": self.create_density_heatmap,
            "density_contour": self.create_density_contour,
            # Matrix or Image Input
            "imshow": self.create_imshow,
            # 3-Dimensional
            "scatter_3d": self.create_scatter_3d_chart,
            "line_3d": self.create_line_3d_chart,
            # Multidimensional
            "scatter_matrix": self.create_scatter_matrix,
            "parallel_coordinates": self.create_parallel_coordinates,
            "parallel_categories": self.create_parallel_categories,
            # Tile Maps
            "scatter_mapbox": self.create_scatter_mapbox,
            "line_mapbox": self.create_line_mapbox,
            "choropleth_mapbox": self.create_choropleth_mapbox,
            "density_mapbox": self.create_density_mapbox,
            # Outline Maps
            "scatter_geo": self.create_scatter_geo,
            "line_geo": self.create_line_geo,
            "choropleth": self.create_choropleth,
            # Polar Charts
            "scatter_polar": self.create_scatter_polar,
            "line_polar": self.create_line_polar,
            "bar_polar": self.create_bar_polar,
            # Ternary Charts
            "scatter_ternary": self.create_scatter_ternary,
            "line_ternary": self.create_line_ternary,
        }

    # Basics
    def create_scatter_chart(self, x, y, **kwargs):
        return px.scatter(self.data, x=x, y=y, **kwargs)

    def create_line_chart(self, x, y, **kwargs):
        return px.line(self.data, x=x, y=y, **kwargs)

    def create_area_chart(self, x, y, **kwargs):
        return px.area(self.data, x=x, y=y, **kwargs)

    def create_bar_chart(self, x, y, **kwargs):
        return px.bar(self.data, x=x, y=y, **kwargs)

    def create_funnel_chart(self, x, y, **kwargs):
        return px.funnel(self.data, x=x, y=y, **kwargs)

    def create_timeline_chart(self, x, y, **kwargs):
        return px.timeline(self.data, x=x, y=y, **kwargs)

    # Part-of-Whole
    def create_pie_chart(self, names, values, **kwargs):
        return px.pie(self.data, names=names, values=values, **kwargs)

    def create_sunburst(self, path, values, **kwargs):
        return px.sunburst(self.data, path=path, values=values, **kwargs)

    def create_treemap(self, path, values, **kwargs):
        return px.treemap(self.data, path=path, values=values, **kwargs)

    def create_icicle_chart(self, path, values, **kwargs):
        return px.icicle(self.data, path=path, values=values, **kwargs)

    def create_funnel_area_chart(self, names, values, **kwargs):
        return px.funnel_area(self.data, names=names, values=values, **kwargs)

    # 1D Distributions
    def create_histogram_chart(self, x, **kwargs):
        return px.histogram(self.data, x=x, **kwargs)

    def create_box_plot(self, x, y, **kwargs):
        return px.box(self.data, x=x, y=y, **kwargs)

    def create_violin_plot(self, x, y, **kwargs):
        return px.violin(self.data, x=x, y=y, **kwargs)

    def create_strip_plot(self, x, y, **kwargs):
        return px.strip(self.data, x=x, y=y, **kwargs)

    def create_ecdf_plot(self, x, **kwargs):
        return px.ecdf(self.data, x=x, **kwargs)

    # 2D Distributions
    def create_density_heatmap(self, x, y, **kwargs):
        return px.density_heatmap(self.data, x=x, y=y, **kwargs)

    def create_density_contour(self, x, y, **kwargs):
        return px.density_contour(self.data, x=x, y=y, **kwargs)

    # Matrix or Image Input
    def create_imshow(self, img, **kwargs):
        return px.imshow(self.data, img=img, **kwargs)

    # 3-Dimensional
    def create_scatter_3d_chart(self, x, y, z, **kwargs):
        return px.scatter_3d(self.data, x=x, y=y, z=z, **kwargs)

    def create_line_3d_chart(self, x, y, z, **kwargs):
        return px.line_3d(self.data, x=x, y=y, z=z, **kwargs)

    # Multidimensional
    def create_scatter_matrix(self, dimensions, **kwargs):
        return px.scatter_matrix(self.data, dimensions=dimensions, **kwargs)

    def create_parallel_coordinates(self, dimensions, **kwargs):
        return px.parallel_coordinates(self.data, dimensions=dimensions, **kwargs)

    def create_parallel_categories(self, dimensions, **kwargs):
        return px.parallel_categories(self.data, dimensions=dimensions, **kwargs)

    # Tile Maps
    def create_scatter_mapbox(self, lat, lon, **kwargs):
        return px.scatter_mapbox(self.data, lat=lat, lon=lon, **kwargs)

    def create_line_mapbox(self, lat, lon, **kwargs):
        return px.line_mapbox(self.data, lat=lat, lon=lon, **kwargs)

    def create_choropleth_mapbox(self, geojson, locations, color, **kwargs):
        return px.choropleth_mapbox(
            self.data, geojson=geojson, locations=locations, color=color, **kwargs
        )

    def create_density_mapbox(self, lat, lon, **kwargs):
        return px.density_mapbox(self.data, lat=lat, lon=lon, **kwargs)

    # Outline Maps
    def create_scatter_geo(self, lat, lon, **kwargs):
        return px.scatter_geo(self.data, lat=lat, lon=lon, **kwargs)

    def create_line_geo(self, lat, lon, **kwargs):
        return px.line_geo(self.data, lat=lat, lon=lon, **kwargs)

    def create_choropleth(self, locations, color, **kwargs):
        return px.choropleth(self.data, locations=locations, color=color, **kwargs)

    # Polar Charts
    def create_scatter_polar(self, r, theta, **kwargs):
        return px.scatter_polar(self.data, r=r, theta=theta, **kwargs)

    def create_line_polar(self, r, theta, **kwargs):
        return px.line_polar(self.data, r=r, theta=theta, **kwargs)

    def create_bar_polar(self, r, theta, **kwargs):
        return px.bar_polar(self.data, r=r, theta=theta, **kwargs)

    # Ternary Charts
    def create_scatter_ternary(self, a, b, c, **kwargs):
        return px.scatter_ternary(self.data, a=a, b=b, c=c, **kwargs)

    def create_line_ternary(self, a, b, c, **kwargs):
        return px.line_ternary(self.data, a=a, b=b, c=c, **kwargs)

    # Create visualization based on type
    def create_visualization(self, chart_type: str, **kwargs):
        """
        Create a Plotly visualization based on the chart type and additional arguments.

        :param chart_type: The type of chart to create (e.g., "bar", "line", "scatter", etc.).
        :param kwargs: Additional arguments required by the specific chart type.
        :return: A Plotly figure.
        """
        chart_func = self.chart_functions.get(chart_type)
        if chart_func:
            return chart_func(**kwargs)
        else:
            st.warning(f"Visualization type '{chart_type}' is not recognized.")
            return None
