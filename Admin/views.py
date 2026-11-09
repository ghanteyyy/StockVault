'''
Public entry points for StockVault's custom administration views
'''
from .user_views import (AdminPage, UserProfile, AddUser, EditUser, DeleteUser,
                         UserChangePassword, ChangeProfile)

from .catalog_views import (AdminListedCompanies, AdminListedCompaniesAdd,
                            AdminListedCompaniesEdit, AdminListedCompaniesDelete,
                            AdminFAQs, AdminFaqAdd, AdminFaqEdit, AdminFaqDelete)

from .operations_views import (AdminOverview, AdminActivity, AdminPortfolios,
                               AdminTransactions,
                               AdminTargets, AdminWishlists)

from .trading_views import (AdminTransactionAdd, AdminTransactionEdit, AdminTransactionDelete,
                            AdminHoldingSave, AdminHoldingDelete)
