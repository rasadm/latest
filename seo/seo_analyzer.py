#!/usr/bin/env python3
"""
SEO Analysis Tool for WordPress Blog Posts
Analyzes existing content and provides comprehensive SEO reports
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from seo.seo_optimizer import MultilingualSEOOptimizer
import argparse

class SEOAnalyzer:
    def __init__(self, content_dir=None, done_dir=None):
        self.seo_optimizer = MultilingualSEOOptimizer()
        self.content_dir = content_dir or os.getenv('CONTENT_DIR', 'serie 1')
        self.done_dir = done_dir or os.getenv('DONE_DIR', 'serie 1/done')
        
    def analyze_single_file(self, file_path: str) -> Dict:
        """Analyze a single markdown file for SEO"""
        
        print(f"🔍 Analyzing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML front matter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    markdown_content = parts[2].strip()
                    
                    try:
                        metadata = yaml.safe_load(yaml_content)
                    except yaml.YAMLError:
                        metadata = {}
                else:
                    metadata = {}
                    markdown_content = content
            else:
                metadata = {}
                markdown_content = content
            
            # Perform comprehensive SEO analysis
            analysis = self.seo_optimizer.analyze_content_comprehensive(markdown_content, metadata)
            
            # Add file information
            analysis['file_info'] = {
                'path': file_path,
                'size_kb': os.path.getsize(file_path) / 1024,
                'last_modified': os.path.getmtime(file_path)
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            return {'error': str(e)}
    
    def analyze_directory(self, directory: str = None) -> Dict:
        """Analyze all markdown files in a directory"""
        
        if directory is None:
            directory = self.content_dir
        
        print(f"📁 Analyzing directory: {directory}")
        
        results = {
            'directory': directory,
            'total_files': 0,
            'analyzed_files': 0,
            'average_seo_score': 0,
            'files': {},
            'summary': {
                'excellent': 0,  # 90-100
                'good': 0,       # 70-89
                'fair': 0,       # 50-69
                'poor': 0        # <50
            },
            'common_issues': [],
            'recommendations': []
        }
        
        # Find all markdown files
        md_files = list(Path(directory).glob('*.md'))
        results['total_files'] = len(md_files)
        
        if not md_files:
            print(f"❌ No markdown files found in {directory}")
            return results
        
        total_score = 0
        all_recommendations = []
        
        for file_path in md_files:
            analysis = self.analyze_single_file(str(file_path))
            
            if 'error' not in analysis:
                results['analyzed_files'] += 1
                seo_score = analysis.get('seo_score', 0)
                total_score += seo_score
                
                # Categorize by score
                if seo_score >= 90:
                    results['summary']['excellent'] += 1
                elif seo_score >= 70:
                    results['summary']['good'] += 1
                elif seo_score >= 50:
                    results['summary']['fair'] += 1
                else:
                    results['summary']['poor'] += 1
                
                # Collect recommendations
                all_recommendations.extend(analysis.get('recommendations', []))
                
                results['files'][str(file_path)] = {
                    'seo_score': seo_score,
                    'title': analysis.get('meta_optimization', {}).get('title', ''),
                    'word_count': analysis.get('content_quality', {}).get('word_count', 0),
                    'readability': analysis.get('structure_readability', {}).get('readability_score', 0),
                    'recommendations_count': len(analysis.get('recommendations', []))
                }
        
        # Calculate averages and common issues
        if results['analyzed_files'] > 0:
            results['average_seo_score'] = total_score / results['analyzed_files']
            
            # Find most common recommendations
            from collections import Counter
            rec_counter = Counter(all_recommendations)
            results['common_issues'] = [
                {'issue': issue, 'frequency': count}
                for issue, count in rec_counter.most_common(10)
            ]
        
        return results
    
    def generate_seo_report(self, analysis: Dict, output_file: str = None) -> str:
        """Generate a comprehensive SEO report"""
        
        report_lines = []
        
        # Header
        report_lines.extend([
            "# SEO Analysis Report",
            f"Generated on: {yaml.safe_load(yaml.dump({'date': 'now'}))['date']}",
            "",
            "## Executive Summary",
            ""
        ])
        
        if 'directory' in analysis:
            # Directory analysis report
            report_lines.extend([
                f"**Directory Analyzed:** {analysis['directory']}",
                f"**Total Files:** {analysis['total_files']}",
                f"**Successfully Analyzed:** {analysis['analyzed_files']}",
                f"**Average SEO Score:** {analysis['average_seo_score']:.1f}/100",
                "",
                "### Score Distribution",
                f"- Excellent (90-100): {analysis['summary']['excellent']} files",
                f"- Good (70-89): {analysis['summary']['good']} files", 
                f"- Fair (50-69): {analysis['summary']['fair']} files",
                f"- Poor (<50): {analysis['summary']['poor']} files",
                "",
                "## Most Common Issues",
                ""
            ])
            
            for i, issue in enumerate(analysis['common_issues'][:5], 1):
                report_lines.append(f"{i}. {issue['issue']} (affects {issue['frequency']} files)")
            
            report_lines.extend([
                "",
                "## File-by-File Analysis",
                ""
            ])
            
            # Sort files by SEO score (lowest first - needs most attention)
            sorted_files = sorted(
                analysis['files'].items(),
                key=lambda x: x[1]['seo_score']
            )
            
            for file_path, file_data in sorted_files:
                filename = Path(file_path).name
                score = file_data['seo_score']
                status = "🔴" if score < 50 else "🟡" if score < 70 else "🟢" if score < 90 else "✅"
                
                report_lines.extend([
                    f"### {status} {filename}",
                    f"- **SEO Score:** {score}/100",
                    f"- **Word Count:** {file_data['word_count']}",
                    f"- **Readability:** {file_data['readability']:.1f}",
                    f"- **Issues Found:** {file_data['recommendations_count']}",
                    ""
                ])
        
        else:
            # Single file analysis report
            report_lines.extend([
                f"**File:** {analysis.get('file_info', {}).get('path', 'Unknown')}",
                f"**SEO Score:** {analysis.get('seo_score', 0)}/100",
                "",
                "## Content Quality Analysis",
                ""
            ])
            
            if 'content_quality' in analysis:
                quality = analysis['content_quality']
                report_lines.extend([
                    f"- **Word Count:** {quality.get('word_count', 0)}",
                    f"- **Unique Words Ratio:** {quality.get('unique_words_ratio', 0):.2f}",
                    f"- **Transition Words:** {quality.get('transition_words_count', 0)}",
                    f"- **Quality Score:** {quality.get('quality_score', 0)}/100",
                    ""
                ])
            
            if 'keyword_optimization' in analysis:
                keyword = analysis['keyword_optimization']
                if 'error' not in keyword:
                    report_lines.extend([
                        "## Keyword Optimization",
                        f"- **Primary Keyword:** {keyword.get('primary_keyword', 'Not specified')}",
                        f"- **Keyword Density:** {keyword.get('primary_density', 0):.2f}%",
                        f"- **Placement Score:** {keyword.get('placement_score', 0)}/100",
                        ""
                    ])
            
            if 'structure_readability' in analysis:
                structure = analysis['structure_readability']
                report_lines.extend([
                    "## Structure & Readability",
                    f"- **Headings:** {len(structure.get('heading_structure', []))}",
                    f"- **Paragraphs:** {structure.get('paragraph_count', 0)}",
                    f"- **Readability Score:** {structure.get('readability_score', 0):.1f}",
                    f"- **Lists:** {structure.get('bullet_lists', 0)} bullet, {structure.get('numbered_lists', 0)} numbered",
                    ""
                ])
            
            if 'technical_seo' in analysis:
                technical = analysis['technical_seo']
                report_lines.extend([
                    "## Technical SEO",
                    f"- **Internal Links:** {technical.get('internal_links', 0)}",
                    f"- **External Links:** {technical.get('external_links', 0)}",
                    f"- **Images:** {technical.get('total_images', 0)} total, {technical.get('images_with_alt', 0)} with alt text",
                    f"- **Alt Text Coverage:** {technical.get('alt_text_coverage', 0):.1f}%",
                    ""
                ])
            
            # Recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                report_lines.extend([
                    "## Recommendations for Improvement",
                    ""
                ])
                
                for i, rec in enumerate(recommendations, 1):
                    report_lines.append(f"{i}. {rec}")
                
                report_lines.append("")
        
        # Generate priority action items
        report_lines.extend([
            "## Priority Action Items",
            "",
            "### High Priority (Fix Immediately)",
            "- Files with SEO score < 50",
            "- Missing meta descriptions",
            "- Images without alt text",
            "- Broken heading hierarchy",
            "",
            "### Medium Priority (Fix This Week)",
            "- Files with SEO score 50-69",
            "- Keyword density issues",
            "- Missing internal links",
            "- Long paragraphs",
            "",
            "### Low Priority (Ongoing Improvement)",
            "- Files with SEO score 70-89",
            "- Readability improvements",
            "- Additional external links",
            "- Schema markup enhancements",
            ""
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 Report saved to: {output_file}")
        
        return report_content
    
    def optimize_file(self, file_path: str, backup: bool = True) -> bool:
        """Optimize a single file for SEO"""
        
        print(f"🔧 Optimizing: {file_path}")
        
        try:
            # Create backup if requested
            if backup:
                backup_path = f"{file_path}.backup"
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"💾 Backup created: {backup_path}")
            
            # Read and parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    markdown_content = parts[2].strip()
                    
                    try:
                        metadata = yaml.safe_load(yaml_content)
                    except yaml.YAMLError:
                        metadata = {}
                else:
                    metadata = {}
                    markdown_content = content
            else:
                metadata = {}
                markdown_content = content
            
            # Extract topic from title or filename
            topic = metadata.get('title', Path(file_path).stem.replace('-', ' ').title())
            
            # Get keywords from existing metadata or generate
            keywords = metadata.get('secondary_keywords', [])
            if not keywords:
                keywords = [topic]
            
            # Generate optimized metadata
            optimized_metadata = self.seo_optimizer.generate_optimized_metadata(
                markdown_content, topic, keywords
            )
            
            # Merge with existing metadata (preserve existing values)
            for key, value in optimized_metadata.items():
                if key not in metadata or not metadata[key]:
                    metadata[key] = value
            
            # Optimize content structure
            optimized_content = self.seo_optimizer.optimize_content_structure(markdown_content)
            
            # Add internal links
            optimized_content = self.seo_optimizer.add_internal_links(optimized_content)
            
            # Reconstruct file
            yaml_output = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
            new_content = f"---\n{yaml_output}---\n\n{optimized_content}"
            
            # Write optimized file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ File optimized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing {file_path}: {e}")
            return False
    
    def batch_optimize(self, directory: str = None, backup: bool = True) -> Dict:
        """Optimize all files in a directory"""
        
        if directory is None:
            directory = self.content_dir
        
        print(f"🔧 Batch optimizing directory: {directory}")
        
        results = {
            'directory': directory,
            'total_files': 0,
            'optimized_files': 0,
            'failed_files': 0,
            'errors': []
        }
        
        # Find all markdown files
        md_files = list(Path(directory).glob('*.md'))
        results['total_files'] = len(md_files)
        
        for file_path in md_files:
            if self.optimize_file(str(file_path), backup):
                results['optimized_files'] += 1
            else:
                results['failed_files'] += 1
                results['errors'].append(str(file_path))
        
        print(f"✅ Batch optimization complete!")
        print(f"   Optimized: {results['optimized_files']}/{results['total_files']} files")
        
        return results

def main():
    """Command-line interface for SEO analyzer"""
    
    parser = argparse.ArgumentParser(description='SEO Analysis Tool for WordPress Blog Posts')
    parser.add_argument('command', choices=['analyze', 'report', 'optimize'], 
                       help='Command to execute')
    parser.add_argument('--file', '-f', help='Specific file to analyze/optimize')
    parser.add_argument('--directory', '-d', default=os.getenv('CONTENT_DIR', 'serie 1'),
                       help='Directory to analyze/optimize (default: from CONTENT_DIR env or serie 1)')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--no-backup', action='store_true', 
                       help='Skip backup when optimizing')
    
    args = parser.parse_args()
    
    analyzer = SEOAnalyzer()
    
    if args.command == 'analyze':
        if args.file:
            # Analyze single file
            analysis = analyzer.analyze_single_file(args.file)
            print(f"\n📊 SEO Score: {analysis.get('seo_score', 0)}/100")
            
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print("\n📋 Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"   {i}. {rec}")
        else:
            # Analyze directory
            analysis = analyzer.analyze_directory(args.directory)
            print(f"\n📊 Analysis Summary:")
            print(f"   Average SEO Score: {analysis['average_seo_score']:.1f}/100")
            print(f"   Files Analyzed: {analysis['analyzed_files']}/{analysis['total_files']}")
            print(f"   Excellent: {analysis['summary']['excellent']}")
            print(f"   Good: {analysis['summary']['good']}")
            print(f"   Fair: {analysis['summary']['fair']}")
            print(f"   Poor: {analysis['summary']['poor']}")
    
    elif args.command == 'report':
        if args.file:
            analysis = analyzer.analyze_single_file(args.file)
        else:
            analysis = analyzer.analyze_directory(args.directory)
        
        output_file = args.output or f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report = analyzer.generate_seo_report(analysis, output_file)
        
        if not args.output:
            print("\n" + "="*50)
            print(report[:1000] + "..." if len(report) > 1000 else report)
    
    elif args.command == 'optimize':
        backup = not args.no_backup
        
        if args.file:
            analyzer.optimize_file(args.file, backup)
        else:
            results = analyzer.batch_optimize(args.directory, backup)
            print(f"\n✅ Optimization Results:")
            print(f"   Optimized: {results['optimized_files']}/{results['total_files']} files")
            if results['errors']:
                print(f"   Errors: {results['failed_files']} files")

if __name__ == "__main__":
    main() 