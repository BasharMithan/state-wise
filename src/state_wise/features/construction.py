"""
Date: 2026, 09, 04

Module: `FeatureConstruction` is a constructor that builds the fatures
needed for the HMM regime detector and the gradient boosting predector.

The made features are:
1. `body-percentage`: The direction of the candle (bullish, bearish).
2. `upper-wick-percentage / lower-wick-percentage`: Measures how far price moved above the body relative
    to the opening level.
3. `log-return`: Measure the differenece between the current candle and the previous one (up or down).
4. `range-percentage`: Calculating the normalized daily trading range as a percentage of the opening price. 

"""


from state_wise.models.schemas import Candle

from math import log


class FeaturesConstruction:
    """A candle features constructor that builds the necessary features for
    the HMM regime detector and the gradient boosting predector.

    Takes a candle, assigns the features to it, return it with the features
    added to it's attributes.
    """
    def __init__(self, candle: Candle) -> None:
        self.candle = candle
        

    def construct(self) -> Candle:

        if self.candle.features:
            self.candle.features.logReturn = self.logReturn()
            self.candle.features.bodyPercentage = self.bodyPercentage()
            self.candle.features.rangePercentage = self.rangePercentage()
            self.candle.features.upperWick = self.upperWick()
            self.candle.features.lowerWick = self.lowerWick()
            self.candle.features.closeLocation = self.closeLocation()

            return self.candle

        # Return the candle with no features if the `candle.features` is None.
        return self.candle



    
    def logReturn(self) -> float:
        """Assigns the log return to the candle

        Returns:
            float: The primary signal of market direction and momentum.
        """

        return log((self.candle.close / self.candle.open))


    
    def bodyPercentage(self) -> float:
        """_summary_

        Returns:
            float: _description_
        """

        return (self.candle.close - self.candle.open) / self.candle.open

    
    def upperWick(self) -> float:
        ...


    
    def lowerWick(self) -> float:
        ...

    
    def rangePercentage(self) -> float:

        return (self.candle.high - self.candle.low) / self.candle.open


    def closeLocation(self) -> float:

        return (self.candle.close - self.candle.low) / (
            self.candle.high - self.candle.low + 0.000001)
    





