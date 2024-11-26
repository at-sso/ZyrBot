from src.env import *


class InterfaceHelper:

    @staticmethod
    def longest_common_substring(s1: str, s2: str) -> str:
        # Use a sliding window approach for efficiency
        max_len: int = 0
        result: str = ""
        len1, len2 = len(s1), len(s2)
        s1, s2 = s1.lower(), s2.lower()
        dp: list[list[int]] = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    if dp[i][j] > max_len:
                        max_len = dp[i][j]
                        result = s1[i - max_len : i]

        return result

    def get_logical_value(self, s: Optional[str], l: StringList) -> str:
        """Returns the actual logical value of the dropdown menus"""
        if s is None:
            return EnvStates.unknown_value.value

        max_common: str = ""
        for s2 in l:
            common: str = self.longest_common_substring(s, s2)
            if len(common) > len(max_common):
                max_common = common

        return max_common


int_helper = InterfaceHelper()
