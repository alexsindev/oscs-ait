-- 1. Insert New Project
-- Type: I/BR - OPT Description: Add a new research project to the system
INSERT INTO rmpo.projects (title, description, keywords, category, research_area, duration_months, contract_start_date, contract_end_date, total_budget, project_status)
VALUES ('AI Ethics Framework', 'Developing ethical guidelines for AI systems', 'AI, Ethics, Framework', 'Research', 'Artificial Intelligence', 24, '2024-01-01', '2025-12-31', 500000.00, 'Active');

-- 2. Update Project Status
-- Type: U/BR - OPT Description: Change project status when milestones are reached
UPDATE rmpo.projects 
SET project_status = 'Completed'
WHERE project_id = 9;

-- 3. Delete Inactive Personnel Assignment
-- Type: D/BR - OPT Description: Remove personnel who are no longer active on projects
DELETE FROM rmpo.project_personnels 
WHERE person_id = 11 AND project_id = 8 AND is_active = 'No';

-- 4. Find All Active Projects
-- Type: BR - OPT Description: List all currently active research projects
SELECT project_id, title, category, contract_start_date, contract_end_date
FROM rmpo.projects 
WHERE project_status = 'Active';

-- 5. Search Projects by Research Area
-- Type: BR - OPT Description: Find projects in specific research domains
SELECT title, description, total_budget
FROM rmpo.projects 
WHERE research_area = 'Biomedical Engineering' AND project_status = 'Active';

-- Business Performance Analysis (BP)

-- 6. Total Budget by Research Area
-- Type: GROUP - BP Description: Analyze budget distribution across research areas
SELECT research_area, COUNT(*) as project_count, SUM(total_budget) as total_funding
FROM rmpo.projects 
GROUP BY research_area
ORDER BY total_funding DESC;

-- 7. Project Success Rate by Category
-- Type: GROUP - BP Description: Calculate completion rates for different project types
SELECT category, 
       COUNT(*) as total_projects,
       COUNT(CASE WHEN project_status = 'Completed' THEN 1 END) as completed_projects,
       ROUND(COUNT(CASE WHEN project_status = 'Completed' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM rmpo.projects 
GROUP BY category;

-- 8. Top Funding Organizations
-- Type: JOIN/GROUP - BP Description: Identify major research sponsors
SELECT ds.organization_name, COUNT(pf.project_id) as projects_funded, SUM(pf.funding_amount) as total_contribution
FROM rmpo.donor_sponsors ds
JOIN rmpo.project_fundings pf ON ds.donor_id = pf.donor_id
GROUP BY ds.donor_id, ds.organization_name
ORDER BY total_contribution DESC
LIMIT 10;

-- Customer/Stakeholder Analysis (CA)

-- 9. Principal Investigators with Most Projects
-- Type: JOIN/GROUP - CA Description: Identify most active research leaders
SELECT p.first_name, p.last_name, p.email, COUNT(pp.project_id) as projects_led
FROM rmpo.people p
JOIN rmpo.project_personnels pp ON p.person_id = pp.person_id
WHERE p.role = 'Principal Investigator'
GROUP BY p.person_id, p.first_name, p.last_name, p.email
ORDER BY projects_led DESC;

-- 10. Department Research Activity
-- Type: JOIN/GROUP - CA Description: Analyze research participation by department
SELECT d.department_name, COUNT(DISTINCT pd.project_id) as active_projects, COUNT(DISTINCT pp.person_id) as researchers_involved
FROM rmpo.departments d
JOIN rmpo.project_departments pd ON d.department_id = pd.department_id
JOIN rmpo.project_personnels pp ON pd.project_id = pp.project_id
WHERE pp.is_active = 'Yes'
GROUP BY d.department_id, d.department_name
ORDER BY active_projects DESC;

-- Basic Trend Analysis (BT)

-- 11. Project Initiation Trends by Year
-- Type: GROUP - BT Description: Track research project growth over time
SELECT YEAR(contract_start_date) as project_year, 
       COUNT(*) as projects_started, 
       SUM(total_budget) as yearly_budget
FROM rmpo.projects 
GROUP BY YEAR(contract_start_date)
ORDER BY project_year DESC;

-- 12. Budget Installment Payment Patterns
-- Type: JOIN/GROUP - BT Description: Analyze payment timing and patterns
SELECT MONTH(installment_date) as payment_month, 
       COUNT(*) as installments_due,
       COUNT(CASE WHEN payment_status = 'Paid' THEN 1 END) as payments_received,
       SUM(amount) as total_amount_due
FROM rmpo.budget_installments 
WHERE YEAR(installment_date) = 2024
GROUP BY MONTH(installment_date)
ORDER BY payment_month;

-- 13. Student Employment Trends
-- Type: JOIN/GROUP - BT Description: Track student research assistant employment over time
SELECT YEAR(pp.start_date) as employment_year, 
       COUNT(*) as students_hired,
       COUNT(DISTINCT pp.project_id) as projects_with_students
FROM rmpo.project_personnels pp
JOIN rmpo.people p ON pp.person_id = p.person_id
WHERE p.person_type = 'Student'
GROUP BY YEAR(pp.start_date)
ORDER BY employment_year DESC;

-- Product Analysis (PA)

-- 14. Project Duration Analysis
-- Type: GROUP - PA Description: Analyze project timeline characteristics
SELECT category,
       AVG(duration_months) as avg_duration_months,
       MIN(duration_months) as shortest_project,
       MAX(duration_months) as longest_project
FROM rmpo.projects 
GROUP BY category;

-- 15. Budget Distribution Analysis
-- Type: GROUP - PA Description: Understand project budget patterns
SELECT 
    CASE 
        WHEN total_budget < 100000 THEN 'Small (< 100K)'
        WHEN total_budget < 500000 THEN 'Medium (100K-500K)'
        ELSE 'Large (> 500K)'
    END as budget_category,
    COUNT(*) as project_count,
    AVG(total_budget) as avg_budget
FROM rmpo.projects 
GROUP BY 
    CASE 
        WHEN total_budget < 100000 THEN 'Small (< 100K)'
        WHEN total_budget < 500000 THEN 'Medium (100K-500K)'
        ELSE 'Large (> 500K)'
    END
ORDER BY avg_budget DESC;

-- 16. Research Area Performance
-- Type: JOIN/GROUP - PA Description: Compare research area outcomes
SELECT p.research_area,
       COUNT(*) as total_projects,
       AVG(p.total_budget) as avg_project_budget,
       COUNT(CASE WHEN p.project_status = 'Completed' THEN 1 END) as completed_count
FROM rmpo.projects p
GROUP BY p.research_area
ORDER BY completed_count DESC;

-- Recommendations (REC)

-- 17. Suggest Collaborators for New Projects
-- Type: JOIN/GROUP - REC Description: Recommend researchers based on expertise and availability
SELECT p.first_name, p.last_name, p.expertise_area, COUNT(pp.project_id) as current_projects
FROM rmpo.people p
LEFT JOIN rmpo.project_personnels pp 
       ON p.person_id = pp.person_id 
      AND pp.is_active = 'Yes'
WHERE (p.expertise_area LIKE '%AI%'
    OR p.expertise_area LIKE '%Machine Learning%'
    OR p.expertise_area LIKE '%Mathematics%')
  AND p.person_type = 'Faculty'
GROUP BY p.person_id, p.first_name, p.last_name, p.expertise_area
HAVING COUNT(pp.project_id) < 3
ORDER BY current_projects ASC;

-- 18. Recommend Funding Sources
-- Type: JOIN/GROUP - REC Description: Suggest donors based on research area alignment
SELECT ds.organization_name, ds.donor_type, COUNT(DISTINCT p.research_area) as research_areas_funded
FROM rmpo.donor_sponsors ds
JOIN rmpo.project_fundings pf ON ds.donor_id = pf.donor_id
JOIN rmpo.projects p ON pf.project_id = p.project_id
WHERE p.research_area IN ('Artificial Intelligence', 'Computer Science')
GROUP BY ds.donor_id, ds.organization_name, ds.donor_type
ORDER BY research_areas_funded DESC;

-- Complex Analysis Queries

-- 19. Project Financial Health Report
-- Type: JOIN/GROUP - BP/BT Description: Comprehensive financial analysis of projects
SELECT p.title, p.total_budget,
       SUM(CASE WHEN bi.payment_status = 'Paid' THEN bi.amount ELSE 0 END) as installments_received,
       (p.total_budget - COALESCE(SUM(CASE WHEN bi.payment_status = 'Paid' THEN bi.amount ELSE 0 END), 0)) as remaining_budget,
       COUNT(CASE WHEN bi.payment_status = 'Paid' THEN bi.installment_id END) as installments_processed
FROM rmpo.projects p
LEFT JOIN rmpo.budget_installments bi ON p.project_id = bi.project_id
WHERE p.project_status = 'Active'
GROUP BY p.project_id, p.title, p.total_budget
ORDER BY remaining_budget DESC;

-- 20. Cross-Department Collaboration Analysis
-- Type: JOIN/GROUP - CA Description: Identify interdisciplinary research patterns
SELECT p.title, COUNT(DISTINCT pd.department_id) as departments_involved,
       GROUP_CONCAT(d.department_name SEPARATOR ', ') as collaborating_departments
FROM rmpo.projects p
JOIN rmpo.project_departments pd ON p.project_id = pd.project_id
JOIN rmpo.departments d ON pd.department_id = d.department_id
GROUP BY p.project_id, p.title
HAVING COUNT(DISTINCT pd.department_id) > 1
ORDER BY departments_involved DESC;

-- Additional Queries for Enhanced Analysis

-- 21. Milestone Progress Analysis
-- Type: JOIN/GROUP - PA Description: Track milestone completion across projects
SELECT p.title, 
       COUNT(m.milestone_id) as total_milestones,
       COUNT(CASE WHEN m.milestone_status = 'Completed' THEN 1 END) as completed_milestones,
       ROUND(AVG(m.completion_percentage), 2) as avg_completion_percentage
FROM rmpo.projects p
LEFT JOIN rmpo.milestones m ON p.project_id = m.project_id
WHERE p.project_status = 'Active'
GROUP BY p.project_id, p.title
ORDER BY avg_completion_percentage DESC;

-- 22. Research Output Productivity Analysis
-- Type: JOIN/GROUP - PA Description: Analyze research output generation
SELECT p.research_area,
       COUNT(DISTINCT p.project_id) as total_projects,
       COUNT(ro.output_id) as total_outputs,
       ROUND(COUNT(ro.output_id) * 1.0 / COUNT(DISTINCT p.project_id), 2) as outputs_per_project
FROM rmpo.projects p
LEFT JOIN rmpo.research_outputs ro ON p.project_id = ro.project_id
GROUP BY p.research_area
ORDER BY outputs_per_project DESC;

-- 23. Faculty Workload Distribution
-- Type: JOIN/GROUP - CA Description: Analyze faculty involvement across projects
SELECT p.first_name, p.last_name, p.expertise_area,
       COUNT(DISTINCT pp.project_id) as projects_involved,
       GROUP_CONCAT(DISTINCT pr.title SEPARATOR '; ') as project_titles
FROM rmpo.people p
JOIN rmpo.project_personnels pp ON p.person_id = pp.person_id
JOIN rmpo.projects pr ON pp.project_id = pr.project_id
WHERE p.person_type = 'Faculty' AND pp.is_active = 'Yes'
GROUP BY p.person_id, p.first_name, p.last_name, p.expertise_area
ORDER BY projects_involved DESC;

-- 24. Funding Diversity Analysis
-- Type: JOIN/GROUP - BP Description: Analyze funding source diversity per project
SELECT p.title,
       COUNT(DISTINCT pf.donor_id) as funding_sources,
       SUM(pf.funding_amount) as total_funding,
       GROUP_CONCAT(ds.organization_name SEPARATOR '; ') as funding_organizations
FROM rmpo.projects p
JOIN rmpo.project_fundings pf ON p.project_id = pf.project_id
JOIN rmpo.donor_sponsors ds ON pf.donor_id = ds.donor_id
WHERE pf.funding_status = 'Active'
GROUP BY p.project_id, p.title
ORDER BY funding_sources DESC;