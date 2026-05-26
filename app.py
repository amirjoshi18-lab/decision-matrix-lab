import os
from flask import Flask, render_template, request, jsonify, make_response
from datetime import datetime

# Enforce clean relative pathing binding for cloud instance environments
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    
    company_name = data.get('companyName', 'Target Startup Operations')
    team_members = data.get('teamMembers', 'Anonymous Researchers')
    solutions = data.get('solutions', [])
    criteria = data.get('criteria', [])
    chosen_index = int(data.get('chosenSolutionIndex', 0))
    chart_image = data.get('chartImage', '')  # Dynamic image string captured from frontend canvas
    
    if not solutions or chosen_index >= len(solutions):
        return jsonify({'error': 'Invalid matrix datasets received'}), 400
        
    chosen_solution = solutions[chosen_index]
    
    # Weights validation
    def normalize_weight(w_val):
        try:
            return float(w_val)
        except (ValueError, TypeError):
            return 0.0

    sorted_criteria = sorted(criteria, key=lambda x: normalize_weight(x.get('weight', 0)), reverse=True)
    top_crit_1 = sorted_criteria[0]['name'] if len(sorted_criteria) > 0 else 'Core Metrics'
    top_crit_2 = sorted_criteria[1]['name'] if len(sorted_criteria) > 1 else 'Secondary Metrics'
    
    chosen_score_on_top = 0
    for c in criteria:
        if c['name'] == top_crit_1:
            chosen_score_on_top = c['scores'][chosen_index]
            break

    score_out_of_max = round(float(chosen_solution['totalScore']), 2)
    
    runner_up_name = "Alternative Options"
    runner_up_score = 0
    for idx, sol in enumerate(solutions):
        if idx != chosen_index and float(sol['totalScore']) > runner_up_score:
            runner_up_score = float(sol['totalScore'])
            runner_up_name = sol['name']
    
    runner_up_score = round(runner_up_score, 2)

    # Content Area 1: Summary Statement
    p1 = f"This document establishes the empirical engineering validation for selecting {chosen_solution['name']} " \
         f"as the primary communication and systems documentation layer for {company_name}. Prepared by lead researchers " \
         f"{team_members}, this technical recommendation summarizes an extensive architectural trade study. Based on a " \
         f"normalized objective calculation framework, {chosen_solution['name']} yielded a definitive performance index of " \
         f"{score_out_of_max} points, outclassing the closest baseline infrastructure alternative, {runner_up_name}, " \
         f"which stalled at {runner_up_score} points. Core tracking indicates this selection is primarily driven by " \
         f"superior stress tolerance in high-weight architectural demands—specifically {top_crit_1} and {top_crit_2}."

    # Content Area 2: Analytical Rationale
    p2 = f"The structural deployment justification of {chosen_solution['name']} is validated by isolating quantitative " \
         f"and qualitative indicators across the evaluation grid. The target solution achieved an elite benchmark score of " \
         f"{chosen_score_on_top}/100 in the critical system performance dimension of {top_crit_1}. This performance ensures immediate " \
         f"mitigation of transactional and scaling risk paths. While competing operational layers failed to support " \
         f"long-term data retention integrity without incurring extensive technical debt, the recommended asset stack provides a " \
         f"sustainable foundation. It successfully aligns deployment constraints with the client's current software development lifecycle (SDLC) goals."

    # BUILD QUANTITATIVE MATRIX DATA TABLE FOR REPORT
    table_rows_html = ""
    total_matrix_weight = 0.0
    sol_raw_totals = [0, 0, 0]
    
    for c in criteria:
        w = normalize_weight(c.get('weight', 0))
        total_matrix_weight += w
        c_scores = c.get('scores', [0, 0, 0])
        
        # Calculate individual weighted scores
        w_score0 = w * c_scores[0]
        w_score1 = w * c_scores[1]
        w_score2 = w * c_scores[2]
        
        sol_raw_totals[0] += c_scores[0]
        sol_raw_totals[1] += c_scores[1]
        sol_raw_totals[2] += c_scores[2]
        
        table_rows_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #cbd5e1; font-weight: 600; text-align: left;">{c['name']}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; font-family: monospace; text-align: center;">{w:.2f}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">{c_scores[0]}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; font-family: monospace; background-color: #f0f7ff; text-align: center; font-weight: bold;">{w_score0:.2f}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">{c_scores[1]}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; font-family: monospace; background-color: #faf5ff; text-align: center; font-weight: bold;">{w_score1:.2f}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">{c_scores[2]}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; font-family: monospace; background-color: #ecfdf5; text-align: center; font-weight: bold;">{w_score2:.2f}</td>
        </tr>
        """

    # Assemble names for table headers safely
    name0 = solutions[0]['name'] if len(solutions) > 0 else "Option 1"
    name1 = solutions[1]['name'] if len(solutions) > 1 else "Option 2"
    name2 = solutions[2]['name'] if len(solutions) > 2 else "Option 3"

    matrix_table_html = f"""
    <div style="margin: 20px 0; overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #cbd5e1; min-w: 800px;">
            <thead>
                <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: left; width: 250px;">Evaluation Criteria Matrix</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; width: 70px;">Weight</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; background-color: #e0f2fe;">{name0}</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; background-color: #bae6fd;">W. Score</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; background-color: #f3e8ff;">{name1}</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; background-color: #e9d5ff;">W. Score</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; background-color: #d1fae5;">{name2}</th>
                    <th style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; background-color: #a7f3d0;">W. Score</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
            <tfoot>
                <tr style="background-color: #e2e8f0; font-weight: bold; border-top: 2px solid #cbd5e1;">
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: left;">TOTAL MATRIX CALCULATIONS</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; font-family: monospace; text-align: center; color: #2563eb;">{total_matrix_weight:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; font-weight: normal;">{sol_raw_totals[0]}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; font-family: monospace; text-align: center; color: #1d4ed8; font-size: 13px;">{solutions[0]['totalScore']:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; font-weight: normal;">{sol_raw_totals[1]}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; font-family: monospace; text-align: center; color: #6b21a8; font-size: 13px;">{solutions[1]['totalScore']:.2f}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; text-align: center; font-weight: normal;">{sol_raw_totals[2]}</td>
                    <td style="padding: 10px; border: 1px solid #cbd5e1; font-family: monospace; text-align: center; color: #065f46; font-size: 13px;">{solutions[2]['totalScore']:.2f}</td>
                </tr>
            </tfoot>
        </table>
    </div>
    """

    # Build qualitative notes block
    bullets_html = ""
    for c in criteria:
        keywords = c.get('keywords', '').strip()
        if keywords:
            score_val = c['scores'][chosen_index]
            bullets_html += f"""
            <div style="margin-bottom: 4px; font-family: sans-serif;">
                <span style="color: #1e3a8a; font-weight: bold; font-size: 13px;">■ Criterion Evaluation: {c['name']}</span> 
                <span style="background-color: #e0f2fe; color: #0369a1; font-size: 11px; font-family: monospace; padding: 1px 5px; border-radius: 4px; margin-left: 6px; font-weight: bold;">Score: {score_val}/100</span>
            </div>
            <div style="padding-left: 12px; color: #475569; font-style: italic; margin-bottom: 16px; border-left: 2px solid #cbd5e1; font-size: 12px;">
                <strong>Student Notes & Observations:</strong> "{keywords}"
            </div>
            """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Inject chart image payload smoothly if captured
    chart_html_block = ""
    if chart_image:
        chart_html_block = f"""
        <h2>📊 Final Weighted Objective Chart</h2>
        <div class="chart-box" style="text-align: center; margin: 25px 0; background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px;">
            <img src="{chart_image}" alt="Final Weighted Objective Chart" style="max-width: 100%; height: auto; display: inline-block;" />
        </div>
        """

    # Assemble unified technical layout payload
    assembled_report_body = f"""
    <div style="border: 1px solid #e2e8f0; padding: 30px; border-radius: 8px; background: #ffffff; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
        <h1 style="color: #1e3a8a; border-bottom: 3px solid #1e3a8a; padding-bottom: 8px; font-size: 22px; text-transform: uppercase; margin-top: 0;">Technical Evaluation Analysis Report</h1>
        <p style="font-size: 13px; color: #475569; margin-bottom: 20px;">
            <strong>Project Target Context:</strong> {company_name} <br>
            <strong>Lead Investigative Evaluators:</strong> {team_members} <br>
            <strong>Analysis Execution Date Log:</strong> {timestamp}
        </p>
        
        <h2>01. Executive Recommendation</h2>
        <p>{p1}</p>
        
        <h2>02. Strategic Justification Vector</h2>
        <p>{p2}</p>
        
        <h2>03. Complete Empirical Analysis Data Grid</h2>
        {matrix_table_html}
        
        {chart_html_block}
        
        <h2>04. Qualitative Student Research Elements</h2>
        <div style="background-color: #f8fafc; padding: 16px; border: 1px solid #cbd5e1; border-radius: 8px; margin-top: 20px;">
            {bullets_html if bullets_html else '<p style="color: #94a3b8; font-style: italic;">No verification notes entered for parameters.</p>'}
        </div>
        
        <span class="meta" style="font-size: 9px; color: #64748b; font-family: monospace; display: block; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 8px; text-transform: uppercase;">System-generated summary verification token via Matrix Analysis Lab.</span>
    </div>
    """

    return jsonify({
        'fullReportHtml': assembled_report_body
    })

@app.route('/download_html', methods=['POST'])
def download_html():
    report_html = request.form.get('htmlContent', '')
    
    printable_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Technical Recommendation Report</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 40px; color: #1e293b; line-height: 1.6; font-size: 13px; }}
            h2 {{ color: #1e3a8a; border-bottom: 2px solid #cbd5e1; padding-bottom: 6px; font-size: 16px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }}
            p {{ text-align: justify; margin-bottom: 12px; color: #334155; }}
            .chart-box {{ text-align: center; margin: 25px 0; background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px; }}
            .chart-box img {{ max-width: 100%; height: auto; display: inline-block; }}
            .meta {{ font-size: 9px; color: #64748b; font-family: monospace; display: block; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 8px; text-transform: uppercase; }}
            @media print {{
                .no-print {{ display: none !important; }}
                body {{ margin: 20px; background: #fff; }}
            }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="no-print" style="background:#f1f5f9; padding:12px; border-radius:6px; margin-bottom:25px; font-family:sans-serif; font-size:12px; color:#475569; display:flex; justify-content:space-between; align-items:center;">
            <span>💡 <strong>Offline Asset Generation Module:</strong> If your print dialogue configuration menu did not open automatically, execute manual extraction via the link option:</span>
            <button onclick="window.print()" style="background:#2563eb; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; cursor:pointer;">Save Asset / Export to PDF</button>
        </div>
        {report_html}
    </body>
    </html>
    """
    
    response = make_response(printable_doc)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=Technical_Recommendation_Report.html'
    return response

if __name__ == '__main__':
    app.run(debug=True)
