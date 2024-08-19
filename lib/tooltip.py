import streamlit as st

def add_tooltips():
    st.markdown("""
                <style>
                    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css');
                </style>
            """, unsafe_allow_html=True)

    tooltip_html = """
                <div class="tooltip">
                    <span class="tooltiptext">
                        <table>
                            <thead>
                                <tr>
                                    <th></th>
                                    <th colspan='2'>AEC</th>
                                    <th colspan='2'>PEM</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td></td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td></tr>
                                <tr><td>Stack lifetime (operating hours)</td><td>60000-90000</td><td>100000-150000</td><td>30000-90000</td><td>100000-150000</td></tr>
                            </tbody>
                        </table>
                        <p>source: IEA, The Future of Hydrogen - Seizing today’s opportunities, International Energy Agency, 2019.</p>
                    </span>
                    <span id="tooltip_trigger">Need help with prospective Stack lifetime data? Check this info  <i class="fas fa-lightbulb"></i></span>
                </div>
            """

    tooltip_html2 = """
                <div class="tooltip">
                    <span class="tooltiptext">
                        <table>
                            <thead>
                                <tr>
                                    <th></th>
                                    <th colspan='2'>AEC</th>
                                    <th colspan='2'>PEM</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td></td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td></tr>
                                <tr><td>Electrical efficiency (%LHV)</td><td>63-70</td><td>70-80</td><td>56-60</td><td>67-74</td></tr>
                            </tbody>
                        </table>
                        <p>source: IEA, The Future of Hydrogen - Seizing today’s opportunities, International Energy Agency, 2019.</p>
                    </span>
                    <span id="tooltip_trigger2">Check current and future efficiency data <i class="fas fa-lightbulb"></i></span>
                </div>
            """

    st.markdown(tooltip_html, unsafe_allow_html=True)
    st.markdown(tooltip_html2, unsafe_allow_html=True)
