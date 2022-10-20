import numpy as np
from local.keyword_value_estimator import lin_ucb
from local.sender_base import SenderBase

class SenderDatasetLevel(SenderBase):
    """Wrapper for the linUCB model.

        Args:
            config['alpha'] (float) : determines the amount of exploration. Larger alpha = more emphasis on upper bound.
    """
    def __init__(self, config, receiver):
        super(SenderDatasetLevel, self).__init__(config, receiver)

        self.model = lin_ucb.LinUCBModel(self.config['alpha'], self)

    def __str__(self):
        return 'dataset_level'

    def generate_query(self, tuple_id, query_length):
        """
            Generate query given current state of model.
        """
        term_list = [splitSignal for signal in self.signalIndex[tuple_id] for splitSignal in
                         signal.splitByAttribute()]

        featurized_terms = np.array([self.featurize_term(x, tuple_id) for x in term_list])
        scores = self.model.predict(featurized_terms)

        return sorted(zip(term_list, scores), key=(lambda x: x[1]), reverse=True)[:query_length]

    def update_model(self, tuple_id, sample_x_signals, sample_y):
        """
            Update state of model.
        """
        sample_x_feat = np.array([self.featurize_term(x, tuple_id) for x in sample_x_signals])
        return self.model.partial_fit(sample_x_feat, sample_y)