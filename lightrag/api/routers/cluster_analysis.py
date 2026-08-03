"""
Cluster analysis and research insights for 3D knowledge graph.

Analyzes entity clusters to generate meaningful labels and demonstrate research value.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


def analyze_cluster_from_data(data: Dict[str, Any], cluster_id: int) -> Dict[str, Any]:
    """Analyze a specific cluster using pre-loaded data."""
    # Get entities in this cluster
    cluster_entities = [e for e in data['entities'] if e['cluster'] == cluster_id]

    if not cluster_entities:
        return {"cluster_id": cluster_id, "error": "No entities found"}

    # Extract keywords from entity names and descriptions
    all_text = ' '.join([
        e['name'] + ' ' + e.get('description', '')[:200]
        for e in cluster_entities
    ]).lower()

    # Common biomedical/research keywords to look for
    keyword_categories = {
        'disease': ['diabetes', 'cancer', 'alzheimer', 'parkinson', 'hypertension', 'obesity', 'disease', 'disorder', 'syndrome'],
        'molecular': ['protein', 'gene', 'mrna', 'dna', 'enzyme', 'receptor', 'kinase', 'antibody'],
        'cellular': ['cell', 'neuron', 'tissue', 'organ', 'mitochondria', 'membrane', 'cytoplasm'],
        'metabolic': ['metabolism', 'glucose', 'insulin', 'lipid', 'cholesterol', 'metabolic', 'pathway'],
        'neuroscience': ['brain', 'neuron', 'synapse', 'neurotransmitter', 'cognitive', 'memory', 'hippocampus'],
        'treatment': ['treatment', 'therapy', 'drug', 'medication', 'intervention', 'clinical', 'trial'],
        'signaling': ['signaling', 'pathway', 'cascade', 'activation', 'inhibition', 'regulation'],
        'genetics': ['gene', 'mutation', 'variant', 'allele', 'genetic', 'genome', 'expression'],
    }

    # Count keyword occurrences
    category_scores = {}
    for category, keywords in keyword_categories.items():
        score = sum(all_text.count(kw) for kw in keywords)
        category_scores[category] = score

    # Determine primary theme
    primary_theme = max(category_scores, key=category_scores.get) if category_scores else 'general'

    # Get top_entities by name length (usually more descriptive)
    top_entities = sorted(cluster_entities, key=lambda e: len(e.get('description', '')), reverse=True)[:5]

    # Generate cluster label based on theme
    theme_labels = {
        'disease': 'Disease & Pathology',
        'molecular': 'Molecular Biology',
        'cellular': 'Cell Biology',
        'metabolic': 'Metabolism & Biochemistry',
        'neuroscience': 'Neuroscience & Brain',
        'treatment': 'Clinical & Therapeutics',
        'signaling': 'Signaling & Pathways',
        'genetics': 'Genetics & Genomics',
    }

    label = theme_labels.get(primary_theme, f'Research Domain {cluster_id}')

    # Calculate cluster statistics
    entity_count = len(cluster_entities)

    # Get edges within cluster
    cluster_entity_ids = {e['id'] for e in cluster_entities}
    internal_edges = [
        edge for edge in data.get('edges', [])
        if (isinstance(edge, list) and len(edge) >= 2 and edge[0] in cluster_entity_ids and edge[1] in cluster_entity_ids) or
           (isinstance(edge, dict) and edge.get('source') in cluster_entity_ids and edge.get('target') in cluster_entity_ids)
    ]

    return {
        'cluster_id': cluster_id,
        'label': label,
        'theme': primary_theme,
        'entity_count': entity_count,
        'internal_edges': len(internal_edges),
        'top_entities': [
            {
                'name': e['name'],
                'description': e.get('description', '')[:150] + '...' if len(e.get('description', '')) > 150 else e.get('description', '')
            }
            for e in top_entities
        ],
        'category_scores': category_scores,
    }


def analyze_cluster(metadata_path: Path, cluster_id: int) -> Dict[str, Any]:
    """Analyze a specific cluster to generate meaningful insights."""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get entities in this cluster
    cluster_entities = [e for e in data['entities'] if e['cluster'] == cluster_id]

    if not cluster_entities:
        return {"cluster_id": cluster_id, "error": "No entities found"}

    # Extract keywords from entity names and descriptions
    all_text = ' '.join([
        e['name'] + ' ' + e.get('description', '')[:200]
        for e in cluster_entities
    ]).lower()

    # Common biomedical/research keywords to look for
    keyword_categories = {
        'disease': ['diabetes', 'cancer', 'alzheimer', 'parkinson', 'hypertension', 'obesity', 'disease', 'disorder', 'syndrome'],
        'molecular': ['protein', 'gene', 'mrna', 'dna', 'enzyme', 'receptor', 'kinase', 'antibody'],
        'cellular': ['cell', 'neuron', 'tissue', 'organ', 'mitochondria', 'membrane', 'cytoplasm'],
        'metabolic': ['metabolism', 'glucose', 'insulin', 'lipid', 'cholesterol', 'metabolic', 'pathway'],
        'neuroscience': ['brain', 'neuron', 'synapse', 'neurotransmitter', 'cognitive', 'memory', 'hippocampus'],
        'treatment': ['treatment', 'therapy', 'drug', 'medication', 'intervention', 'clinical', 'trial'],
        'signaling': ['signaling', 'pathway', 'cascade', 'activation', 'inhibition', 'regulation'],
        'genetics': ['gene', 'mutation', 'variant', 'allele', 'genetic', 'genome', 'expression'],
    }

    # Count keyword occurrences
    category_scores = {}
    for category, keywords in keyword_categories.items():
        score = sum(all_text.count(kw) for kw in keywords)
        category_scores[category] = score

    # Determine primary theme
    primary_theme = max(category_scores, key=category_scores.get) if category_scores else 'general'

    # Get top entities by name length (usually more descriptive)
    top_entities = sorted(cluster_entities, key=lambda e: len(e.get('description', '')), reverse=True)[:5]

    # Generate cluster label based on theme
    theme_labels = {
        'disease': 'Disease & Pathology',
        'molecular': 'Molecular Biology',
        'cellular': 'Cell Biology',
        'metabolic': 'Metabolism & Biochemistry',
        'neuroscience': 'Neuroscience & Brain',
        'treatment': 'Clinical & Therapeutics',
        'signaling': 'Signaling & Pathways',
        'genetics': 'Genetics & Genomics',
    }

    label = theme_labels.get(primary_theme, f'Research Domain {cluster_id}')

    # Calculate cluster statistics
    entity_count = len(cluster_entities)

    # Get edges within cluster
    cluster_entity_ids = {e['id'] for e in cluster_entities}
    internal_edges = [
        edge for edge in data.get('edges', [])
        if (isinstance(edge, list) and len(edge) >= 2 and edge[0] in cluster_entity_ids and edge[1] in cluster_entity_ids) or
           (isinstance(edge, dict) and edge.get('source') in cluster_entity_ids and edge.get('target') in cluster_entity_ids)
    ]

    return {
        'cluster_id': cluster_id,
        'label': label,
        'theme': primary_theme,
        'entity_count': entity_count,
        'internal_edges': len(internal_edges),
        'top_entities': [
            {
                'name': e['name'],
                'description': e.get('description', '')[:150] + '...' if len(e.get('description', '')) > 150 else e.get('description', '')
            }
            for e in top_entities
        ],
        'category_scores': category_scores,
    }


def generate_research_insights(metadata_path: Path) -> Dict[str, Any]:
    """Generate overall research insights about the knowledge graph."""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entity_count = data['entity_count']
    edge_count = data['edge_count']
    cluster_count = data['cluster_count']

    # Calculate average connections per entity
    avg_connections = edge_count * 2 / entity_count if entity_count > 0 else 0

    # Analyze cluster distribution
    cluster_sizes = Counter(e['cluster'] for e in data['entities'])
    largest_cluster = cluster_sizes.most_common(1)[0] if cluster_sizes else (0, 0)
    smallest_cluster = cluster_sizes.most_common()[-1] if cluster_sizes else (0, 0)

    # Generate insights
    insights = [
        {
            'icon': '🔬',
            'title': 'Comprehensive Knowledge Base',
            'description': f'This graph contains {entity_count:,} entities and {edge_count:,} relationships, representing a comprehensive knowledge base extracted from research literature.'
        },
        {
            'icon': '🎯',
            'title': 'Semantic Clustering',
            'description': f'Entities are organized into {cluster_count} semantic clusters using dimensionality reduction, grouping related concepts together for easier exploration.'
        },
        {
            'icon': '🔗',
            'title': 'Hidden Connections',
            'description': f'With an average of {avg_connections:.1f} connections per entity, the graph reveals hidden relationships between concepts that might not be obvious from individual papers.'
        },
        {
            'icon': '🧬',
            'title': 'Cross-Disciplinary Insights',
            'description': 'The knowledge graph spans multiple research domains, enabling discovery of cross-disciplinary connections and novel research hypotheses.'
        },
        {
            'icon': '💡',
            'title': 'Research Acceleration',
            'description': 'By visualizing the entire knowledge space, researchers can quickly identify gaps, find relevant work, and avoid duplicating existing research.'
        },
        {
            'icon': '📊',
            'title': 'Data-Driven Discovery',
            'description': f'The largest cluster contains {largest_cluster[1]:,} entities, indicating a major research focus area. Explore clusters to identify emerging trends.'
        },
    ]

    return {
        'total_entities': entity_count,
        'total_edges': edge_count,
        'total_clusters': cluster_count,
        'avg_connections_per_entity': round(avg_connections, 1),
        'largest_cluster': {'id': largest_cluster[0], 'size': largest_cluster[1]},
        'smallest_cluster': {'id': smallest_cluster[0], 'size': smallest_cluster[1]},
        'insights': insights,
        'use_cases': [
            {
                'title': 'Literature Review',
                'description': 'Quickly understand the landscape of a research field by exploring entity clusters and their connections.',
                'example': 'Click on a cluster to see related entities, then query specific topics to see how they connect.'
            },
            {
                'title': 'Hypothesis Generation',
                'description': 'Discover unexpected connections between entities that suggest new research directions.',
                'example': 'Query two seemingly unrelated concepts and see if the graph reveals hidden pathways between them.'
            },
            {
                'title': 'Gap Identification',
                'description': 'Identify areas with sparse connections that may represent research opportunities.',
                'example': 'Look for entities with few connections or clusters that are isolated from the main network.'
            },
            {
                'title': 'Cross-Disciplinary Research',
                'description': 'Find connections between different research domains that could lead to novel insights.',
                'example': 'Explore how entities from different clusters (e.g., neuroscience and metabolism) are connected.'
            },
        ]
    }


def get_all_cluster_analyses(metadata_path: Path) -> List[Dict[str, Any]]:
    """Analyze all clusters and return summary."""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cluster_ids = sorted(set(e['cluster'] for e in data['entities']))
    # Analyze ALL clusters (previously limited to 20, causing mismatches)
    # Using pre-loaded data for performance
    analyses = [analyze_cluster_from_data(data, cid) for cid in cluster_ids]

    return analyses
