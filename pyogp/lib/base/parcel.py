# standard python modules
from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG

# related
from eventlet import api

# pyogp
from pyogp.lib.base.settings import Settings

# pyogp messaging
from pyogp.lib.base.message.packets import *

# utilities
from pyogp.lib.base.utilities.helpers import Helpers

# pyogp messaging

# pyogp utilities

# initialize logging
logger = getLogger('pyogp.lib.base.parcel')
log = logger.log

# ToDo: unhandled related messages
#   ForceObjectSelect
#   ParcelBuyPass
#   ParcelAccessListUpdate
#   ParcelDwellRequest
#   ParcelDwellReply
#   ParcelGodMarkAsContent
#   ViewerStartAuction
#   ParcelObjectOwnersRequest
#   ParcelObjectOwnersReply

# non client oriented related messages
#   #RequestParcelTransfer (sim->dataserver)
#   #UpdateParcel (sim->dataserver)
#   #RemoveParcel (sim->dataserver)
#   #MergeParcel (sim->dataserver)
#   #LogParcelChanges (sim->dataserver)
#   #CheckParcelSales (sim->dataserver)
#   #ParcelSales (dataserver->sim)
#   #StartAuction (sim->dataserver)
#   #ConfirmAuctionStart (dataserver->sim)
#   #CompleteAuction (sim->dataserver)
#   #CancelAuction (sim->dataserver)
#   #CheckParcelAuctions (sim->dataserver)
#   #ParcelAuctions (dataserver->sim)

class ParcelManager(object):
    """ a parcel manager, generally used as an attribute of a region """

    def __init__(self, region = None, agent = None, packet_handler = None, events_handler = None, settings = None):
        """ initialize the parcel manager """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        # store the incoming parameters
        self.region = region
        self.agent = agent
        self.packet_handler = packet_handler

        # otherwise, let's just use our own
        if events_handler != None:
            self.events_handler = events_handler
        else:
            self.events_handler = EventsHandler()

        self.helpers = Helpers()

        # initialize the parcel storage container
        self.parcels = []
        # initialize the parcel overlay storage container
        self.parcel_overlay = {}

        # set up callbacks for parcel related packets
        self.onParcelOverlay_received = self.packet_handler._register('ParcelOverlay')
        self.onParcelOverlay_received.subscribe(self.onParcelOverlay)

        self.onParcelProperties_received = self.agent.event_queue_handler._register('ParcelProperties')
        self.onParcelProperties_received.subscribe(self.onParcelProperties)

        self.onParcelPropertiesUpdate_received = self.packet_handler._register('ParcelPropertiesUpdate')
        self.onParcelPropertiesUpdate_received.subscribe(self.onParcelPropertiesUpdate)

        self.onParcelInfoReply_received = self.packet_handler._register('ParcelInfoReply')
        self.onParcelInfoReply_received.subscribe(self.onParcelInfoReply)

        if self.settings.LOG_VERBOSE: log(DEBUG, "Initializing the parcel manager for %s in region %s." % (self.agent.Name(), self.region.SimName))

    def onParcelOverlay(self, packet):
        """ parse and handle an incoming ParcelOverlay packet

        Currently, we store this data in the ParcelManager.packet_overlay dictionary
        as parcel_overlay[sequence_id] = data (unparsed binary)
        """

        # unpack the data
        sequence_id = packet.message_data.blocks['ParcelData'][0].get_variable('SequenceID').data
        data = packet.message_data.blocks['ParcelData'][0].get_variable('Data').data

        # store the data
        # ToDo: make sense of the binary blob in data
        self.parcel_overlay[sequence_id] = data

    def onParcelProperties(self, packet):
        """ parse and handle an incoming ParcelProperties packet. Parse and serialize the info into a Parcel() representation, then store it (or replace the stored version) """

        RequestResult =  packet.message_data.blocks['ParcelData'][0].get_variable('RequestResult').data
        SequenceID =  packet.message_data.blocks['ParcelData'][0].get_variable('SequenceID').data
        SnapSelection=  packet.message_data.blocks['ParcelData'][0].get_variable('SnapSelection').data
        SelfCount =  packet.message_data.blocks['ParcelData'][0].get_variable('SelfCount').data
        OtherCount =  packet.message_data.blocks['ParcelData'][0].get_variable('OtherCount').data
        PublicCount =  packet.message_data.blocks['ParcelData'][0].get_variable('PublicCount').data
        LocalID =  packet.message_data.blocks['ParcelData'][0].get_variable('LocalID').data
        OwnerID =  packet.message_data.blocks['ParcelData'][0].get_variable('OwnerID').data
        IsGroupOwned =  packet.message_data.blocks['ParcelData'][0].get_variable('IsGroupOwned').data
        AuctionID =  packet.message_data.blocks['ParcelData'][0].get_variable('AuctionID').data
        ClaimDate =  packet.message_data.blocks['ParcelData'][0].get_variable('ClaimDate').data
        ClaimPrice =  packet.message_data.blocks['ParcelData'][0].get_variable('ClaimPrice').data
        RentPrice =  packet.message_data.blocks['ParcelData'][0].get_variable('RentPrice').data
        AABBMin =  packet.message_data.blocks['ParcelData'][0].get_variable('AABBMin').data
        AABBMax =  packet.message_data.blocks['ParcelData'][0].get_variable('AABBMax').data
        Bitmap =  packet.message_data.blocks['ParcelData'][0].get_variable('Bitmap').data
        Area =  packet.message_data.blocks['ParcelData'][0].get_variable('Area').data
        Status =  packet.message_data.blocks['ParcelData'][0].get_variable('Status').data
        SimWideMaxPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('SimWideMaxPrims').data
        SimWideTotalPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('SimWideTotalPrims').data
        MaxPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('MaxPrims').data
        TotalPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('TotalPrims').data
        OwnerPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('OwnerPrims').data
        GroupPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('GroupPrims').data
        OtherPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('OtherPrims').data
        SelectedPrims =  packet.message_data.blocks['ParcelData'][0].get_variable('SelectedPrims').data
        ParcelPrimBonus =  packet.message_data.blocks['ParcelData'][0].get_variable('ParcelPrimBonus').data
        OtherCleanTime =  packet.message_data.blocks['ParcelData'][0].get_variable('OtherCleanTime').data
        ParcelFlags =  packet.message_data.blocks['ParcelData'][0].get_variable('ParcelFlags').data
        SalePrice =  packet.message_data.blocks['ParcelData'][0].get_variable('SalePrice').data
        Name =  packet.message_data.blocks['ParcelData'][0].get_variable('Name').data
        Desc =  packet.message_data.blocks['ParcelData'][0].get_variable('Desc').data
        MusicURL =  packet.message_data.blocks['ParcelData'][0].get_variable('MusicURL').data
        MediaURL =  packet.message_data.blocks['ParcelData'][0].get_variable('MediaURL').data
        MediaID =  packet.message_data.blocks['ParcelData'][0].get_variable('MediaID').data
        MediaAutoScale =  packet.message_data.blocks['ParcelData'][0].get_variable('MediaAutoScale').data
        GroupID =  packet.message_data.blocks['ParcelData'][0].get_variable('GroupID').data
        PassPrice =  packet.message_data.blocks['ParcelData'][0].get_variable('PassPrice').data
        PassHours =  packet.message_data.blocks['ParcelData'][0].get_variable('PassHours').data
        Category =  packet.message_data.blocks['ParcelData'][0].get_variable('Category').data
        AuthBuyerID =  packet.message_data.blocks['ParcelData'][0].get_variable('AuthBuyerID').data
        SnapshotID =  packet.message_data.blocks['ParcelData'][0].get_variable('SnapshotID').data
        UserLocation =  packet.message_data.blocks['ParcelData'][0].get_variable('UserLocation').data
        UserLookAt =  packet.message_data.blocks['ParcelData'][0].get_variable('UserLookAt').data
        LandingType =  packet.message_data.blocks['ParcelData'][0].get_variable('LandingType').data
        RegionPushOverride =  packet.message_data.blocks['ParcelData'][0].get_variable('RegionPushOverride').data
        RegionDenyAnonymous =  packet.message_data.blocks['ParcelData'][0].get_variable('RegionDenyAnonymous').data
        RegionDenyIdentified =  packet.message_data.blocks['ParcelData'][0].get_variable('RegionDenyIdentified').data
        RegionDenyTransacted =  packet.message_data.blocks['ParcelData'][0].get_variable('RegionDenyTransacted').data
        RegionDenyAgeUnverified =  packet.message_data.blocks['AgeVerificationBlock'][0].get_variable('RegionDenyAgeUnverified').data

        parcel = Parcel(self.region, self.agent, RequestResult = RequestResult, SequenceID = SequenceID, SnapSelection = SnapSelection, SelfCount = SelfCount, OtherCount = OtherCount, PublicCount = PublicCount, LocalID = LocalID, OwnerID = OwnerID, IsGroupOwned = IsGroupOwned, AuctionID = AuctionID, ClaimDate = ClaimDate, ClaimPrice = ClaimPrice, RentPrice = RentPrice, AABBMin = AABBMin, AABBMax = AABBMax, Bitmap = Bitmap, Area = Area, Status = Status, SimWideMaxPrims = SimWideMaxPrims, SimWideTotalPrims = SimWideTotalPrims, MaxPrims = MaxPrims, TotalPrims = TotalPrims, OwnerPrims = OwnerPrims, GroupPrims = GroupPrims, OtherPrims = OtherPrims, SelectedPrims = SelectedPrims, ParcelPrimBonus = ParcelPrimBonus, OtherCleanTime = OtherCleanTime, ParcelFlags = ParcelFlags, SalePrice = SalePrice, Name = Name, Desc = Desc, MusicURL = MusicURL, MediaURL = MediaURL, MediaID = MediaID, MediaAutoScale = MediaAutoScale, GroupID = GroupID, PassPrice = PassPrice, PassHours = PassHours, Category = Category, AuthBuyerID = AuthBuyerID, SnapshotID = SnapshotID, UserLocation = UserLocation, UserLookAt = UserLookAt, LandingType = LandingType, RegionPushOverride = RegionPushOverride, RegionDenyAnonymous = RegionDenyAnonymous, RegionDenyIdentified = RegionDenyIdentified, RegionDenyTransacted = RegionDenyTransacted, RegionDenyAgeUnverified = RegionDenyAgeUnverified, settings = self.settings)

        self._store_parcel(parcel)

    def onParcelPropertiesUpdate(self, packet):
        """ parse and handle an incoming ParcelPropertiesUpdate packet. parse the data into a dictionary and pass the blob to the Parcel() instance for self handling """

        parcel_update = {}

        parcel_update['LocalID'] = packet.message_data.blocks['ParcelData'][0].get_variable('LocalID').data
        parcel_update['Flags'] = packet.message_data.blocks['ParcelData'][0].get_variable('Flags').data
        parcel_update['ParcelFlags'] = packet.message_data.blocks['ParcelData'][0].get_variable('ParcelFlags').data
        parcel_update['SalePrice'] = packet.message_data.blocks['ParcelData'][0].get_variable('SalePrice').data
        parcel_update['Name'] = packet.message_data.blocks['ParcelData'][0].get_variable('Name').data
        parcel_update['Desc'] = packet.message_data.blocks['ParcelData'][0].get_variable('Desc').data
        parcel_update['MusicURL'] = packet.message_data.blocks['ParcelData'][0].get_variable('MusicURL').data
        parcel_update['MediaURL'] = packet.message_data.blocks['ParcelData'][0].get_variable('MediaURL').data
        parcel_update['MediaID'] = packet.message_data.blocks['ParcelData'][0].get_variable('MediaID').data
        parcel_update['MediaAutoScale'] = packet.message_data.blocks['ParcelData'][0].get_variable('MediaAutoScale').data
        parcel_update['GroupID'] = packet.message_data.blocks['ParcelData'][0].get_variable('GroupID').data
        parcel_update['PassPrice'] = packet.message_data.blocks['ParcelData'][0].get_variable('PassPrice').data
        parcel_update['PassHours'] = packet.message_data.blocks['ParcelData'][0].get_variable('PassHours').data
        parcel_update['Category'] = packet.message_data.blocks['ParcelData'][0].get_variable('Category').data
        parcel_update['AuthBuyerID'] = packet.message_data.blocks['ParcelData'][0].get_variable('AuthBuyerID').data
        parcel_update['SnapshotID'] = packet.message_data.blocks['ParcelData'][0].get_variable('SnapshotID').data
        parcel_update['UserLocation'] = packet.message_data.blocks['ParcelData'][0].get_variable('UserLocation').data
        parcel_update['UserLookAt'] = packet.message_data.blocks['ParcelData'][0].get_variable('UserLookAt').data
        parcel_update['LandingType'] = packet.message_data.blocks['ParcelData'][0].get_variable('LandingType').data

        self._update_parcel_properties(parcel_update)

    def _store_parcel(self, new_parcel):
        """ store a representation of a parcel """

        # replace an existing list member, else, append

        index = [self.parcels.index(parcel) for parcel in self.parcels if parcel.LocalID == new_parcel.LocalID]

        if index != []:

            self.parcels[index[0]] = new_parcel

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Updating a stored parcel: %s in region \'%s\'' % (new_parcel.LocalID, self.region.SimName))

        else:

            self.parcels.append(new_parcel)

            if self.settings.LOG_VERBOSE: log(DEBUG, 'Stored a new parcel: %s in region \'%s\'' % (new_parcel.LocalID, self.region.SimName))

    def _update_parcel_properties(self, parcel_properties):
        """ update a stored parcel's properties. finds the stored parcel and passes it a dictionary to process """

        parcels_found = []

        if parcel_properties.has_key('LocalID'):

            LocalID = parcel_properties['LocalID']

            parcels_found = [parcel for parcel in self.parcels if str(parcel.LocalID) == str(LocalID)]

            if len(parcels_found) == 0:

                log(INFO, "Received ParcelPropertiesUpdate for parcel we do not know about yet. Storing a partial representation.")

                new_parcel = Parcel(self.region, self.agent, LocalID = parcel_properties['LocalID'], Flags = parcel_properties['Flags'], ParcelFlags = parcel_properties['ParcelFlags'], SalePrice = parcel_properties['SalePrice'], Name = parcel_properties['Name'], Desc = parcel_properties['Desc'], MusicURL = parcel_properties['MusicURL'], MediaURL = parcel_properties['MediaURL'], MediaID = parcel_properties['MediaID'], MediaAutoScale = parcel_properties['MediaAutoScale'], GroupID = parcel_properties['GroupID'], PassPrice = parcel_properties['PassPrice'], PassHours = parcel_properties['PassHours'], Category = parcel_properties['Category'], AuthBuyerID = parcel_properties['AuthBuyerID'], SnapshotID = parcel_properties['SnapshotID'], UserLocation = parcel_properties['UserLocation'], UserLookAt = parcel_properties['UserLookAt'], LandingType = parcel_properties['LandingType'], settings = self.settings)

                self._store_parcel(new_parcel)

            elif len(parcels_found) == 1:

                parcel = parcels_found[0]

                parcel._update_properties(parcel_properties)

        elif parcel_properties.has_key('ParcelID'):

            ParcelID = parcel_properties['ParcelID']

            parcels_found = [parcel for parcel in self.parcels if str(parcel.ParcelID) == str(ParcelID)]

            if len(parcels_found) == 0:

                log(INFO, "Received ParcelPropertiesUpdate for parcel we do not know about yet. Storing a partial representation.")

                new_parcel = Parcel(self.region, self.agent, LocalID = parcel_properties['LocalID'], Flags = parcel_properties['Flags'], ParcelFlags = parcel_properties['ParcelFlags'], SalePrice = parcel_properties['SalePrice'], Name = parcel_properties['Name'], Desc = parcel_properties['Desc'], MusicURL = parcel_properties['MusicURL'], MediaURL = parcel_properties['MediaURL'], MediaID = parcel_properties['MediaID'], MediaAutoScale = parcel_properties['MediaAutoScale'], GroupID = parcel_properties['GroupID'], PassPrice = parcel_properties['PassPrice'], PassHours = parcel_properties['PassHours'], Category = parcel_properties['Category'], AuthBuyerID = parcel_properties['AuthBuyerID'], SnapshotID = parcel_properties['SnapshotID'], UserLocation = parcel_properties['UserLocation'], UserLookAt = parcel_properties['UserLookAt'], LandingType = parcel_properties['LandingType'], settings = self.settings)

                self._store_parcel(new_parcel)

            elif len(parcels_found) == 1:

                parcel = parcels_found[0]

                parcel._update_properties(parcel_properties)

    def request_estate_covenant(self, ):
        """ request the estate covenant (for the current estate)"""

        self.onEstateCovenantReply_received = self.packet_handler._register('EstateCovenantReply')
        self.onEstateCovenantReply_received.subscribe(self.onEstateCovenantReply)

        self.sendEstateCovenantRequest()

    def sendEstateCovenantRequest(self):
        """ send an EstateCovenantRequest packet """

        packet = EstateCovenantRequestPacket()

        packet.AgentData['AgentID'] = self.agent.agent_id
        packet.AgentData['SessionID'] = self.agent.session_id

        self.region.enqueue_message(packet)

    def onEstateCovenantReply(self, packet):
        """ parse and handle an EstateCovenantReply packet """

        try:

            self.onEstateCovenantReply_received.unsubscribe(self.onEstateCovenantReply)

        except AttributeError:

            pass

        CovenantID =  packet.message_data.blocks['Data'][0].get_variable('CovenantID').data
        CovenantTimestamp =  packet.message_data.blocks['Data'][0].get_variable('CovenantTimestamp').data
        EstateName =  packet.message_data.blocks['Data'][0].get_variable('EstateName').data
        EstateOwnerID =  packet.message_data.blocks['Data'][0].get_variable('EstateOwnerID').data

        log(INFO, "Received EstateCovenantReply for estate name %s with a CovenantID of %s." % (EstateName, CovenantID))

        # storing this data as a dict in the parcel manager until we have something better to do with it
        self.estatecovenantreply = {'CovenantID': CovenantID, 'CovenantTimestamp': CovenantTimestamp, 'EstateName': EstateName, 'EstateOwnerID': EstateOwnerID}

    def sendParcelPropertiesRequest(self, SequenceID, West, South, East, North, SnapSelection):
        """ sends a ParcelPropertiesRequest packet """

        packet = ParcelPropertiesRequestPacket()

        packet.AgentData['AgentID'] = self.agent.agent_id
        packet.AgentData['SessionID'] = self.agent.session_id

        packet.ParcelData['SequenceID'] = SequenceID
        packet.ParcelData['West'] = West
        packet.ParcelData['South'] = South
        packet.ParcelData['East'] = East
        packet.ParcelData['North'] = North
        packet.ParcelData['SnapSelection'] = SnapSelection

        self.region.enqueue_message(packet)

    def sendParcelPropertiesRequestByID(self, SequenceID, LocalID):
        """ sends a ParcelPropertiesRequestByID packet """

        packet = ParcelPropertiesRequestByID()

        packet.AgentData['AgentID'] = self.agent.agent_id
        packet.AgentData['SessionID'] = self.agent.session_id

        packet.ParcelData['SequenceID'] = SequenceID
        packet.ParcelData['LocalID'] = LocalID

        self.region.enqueue_message(packet)

    def request_parcel_info(self, parcel_id):
        """ request information for a parcel by id """

        if type(parcel_id) == str:

            try:

                parcel_id = UUID(parcel_id)

            except ValueError:

                log(WARNING, 'Parcel_id passed to request_parcel_info must but a valid UUID or string representation of a uuid. %s was passed in' % (parcel_id))

                return

        elif not isinstance(parcel_id, UUID):

            log(WARNING, 'Parcel_id passed to request_parcel_info must but a valid UUID or string representation of a uuid. %s was passed in' % (parcel_id))

            return

        self.sendParcelInfoRequest(parcel_id)

    def sendParcelInfoRequest(self, parcel_id):
        """ send a ParcelInfoRequest packet for the specified parcelid """

        packet = ParcelInfoRequestPacket()

        # build the agent data block
        packet.AgentData['AgentID'] = self.agent.agent_id
        packet.AgentData['SessionID'] = self.agent.session_id

        packet.Data['ParcelID'] = parcel_id

        self.region.enqueue_message(packet)

    def onParcelInfoReply(self, packet):
        """ parse and handle a ParcelInfoReply packet """

        parcel_info = {}

        parcel_info['ParcelID'] = packet.message_data.blocks['Data'][0].get_variable('ParcelID').data
        parcel_info['OwnerID'] = packet.message_data.blocks['Data'][0].get_variable('OwnerID').data
        parcel_info['Name'] = packet.message_data.blocks['Data'][0].get_variable('Name').data
        parcel_info['Desc'] = packet.message_data.blocks['Data'][0].get_variable('Desc').data
        parcel_info['ActualArea'] = packet.message_data.blocks['Data'][0].get_variable('ActualArea').data
        parcel_info['BillableArea'] = packet.message_data.blocks['Data'][0].get_variable('BillableArea').data
        parcel_info['Flags'] = packet.message_data.blocks['Data'][0].get_variable('Flags').data
        parcel_info['GlobalX'] = packet.message_data.blocks['Data'][0].get_variable('GlobalX').data
        parcel_info['GlobalY'] = packet.message_data.blocks['Data'][0].get_variable('GlobalY').data
        parcel_info['GlobalZ'] = packet.message_data.blocks['Data'][0].get_variable('GlobalZ').data
        parcel_info['SimName'] = packet.message_data.blocks['Data'][0].get_variable('SimName').data
        parcel_info['SnapshotID'] = packet.message_data.blocks['Data'][0].get_variable('SnapshotID').data
        parcel_info['Dwell'] = packet.message_data.blocks['Data'][0].get_variable('Dwell').data
        parcel_info['SalePrice'] = packet.message_data.blocks['Data'][0].get_variable('SalePrice').data
        parcel_info['AuctionID'] = packet.message_data.blocks['Data'][0].get_variable('AuctionID').data

        self._update_parcel_properties(parcel_info)

    def request_current_parcel_properties(self):
        """ request the properties of the parcel the agent currently inhabits """

        self.SouthWest = self.agent.Position.X
        self.NorthEast = self.agent.Position.Y

        self.sendParcelPropertiesRequest(-50000, self.SouthWest, self.SouthWest, self.NorthEast, self.NorthEast, False)

    def request_all_parcel_properties(self, delay = 1):
        """ request the properties of all of the parcels on the current region. The delay parameter is a sleep between the send of each packet request """

        # spawn a coroutine so this is non blocking
        api.spawn(self.__request_all_parcel_properties, delay)

    def __request_all_parcel_properties(self, delay = 1):
        """ request the properties of all of the parcels on the current region """

        # ugh this is a wretched way to request parcel info, but it is what it is
        for x in range(1,17):
            for y in range(1,17):

                self.sendParcelPropertiesRequest(-50000, x * 4, x * 4, y * 4, y * 4, False)

                api.sleep(delay)

    def return_parcel_objects(self, ):
        """ return the specified objects for the specified parcel """

        pass

        '''
        // ParcelReturnObjects
        // viewer -> sim
        // reliable
        {
        	ParcelReturnObjects Low 199 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def disable_objects(self, ):
        """ set objects nonphysical and disable scripts for the specified parcel """

        pass

        '''
        // Disable makes objects nonphysical and turns off their scripts.
        // ParcelDisableObjects
        // viewer -> sim
        // reliable
        {
        	ParcelDisableObjects Low 201 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
            {
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def sendParcelDisableObjects(self, ):
        """ send a ParcelDisableObjects packet """

        pass

        '''
        // Disable makes objects nonphysical and turns off their scripts.
        // ParcelDisableObjects
        // viewer -> sim
        // reliable
        {
        	ParcelDisableObjects Low 201 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
            {
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def join_parcels(self, ):
        """ joins the specified parcels """

        pass

        '''
        // ParcelJoin - Take all parcels which are owned by agent and inside
        // rectangle, and make them 1 parcel if they all are leased.
        // viewer -> sim
        // reliable
        {
        	ParcelJoin Low 210 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        
        '''

    def sendParcelJoin(self, ):
        """ send a ParcelJoin packet """

        pass

        '''
        // ParcelJoin - Take all parcels which are owned by agent and inside
        // rectangle, and make them 1 parcel if they all are leased.
        // viewer -> sim
        // reliable
        {
        	ParcelJoin Low 210 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        '''

    def divide_parcel(self, ):
        """ divide the selection into a new parcel """

        pass

        '''
        // ParcelDivide
        // If the selection is a subsection of exactly one parcel,
        // chop out that section and make a new parcel of it.
        // viewer -> sim
        // reliable
        {
        	ParcelDivide Low 211 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        '''

    def sendParcelDivide(self, ):
        """ send a ParcelDivide packet """

        pass

        '''
        // ParcelDivide
        // If the selection is a subsection of exactly one parcel,
        // chop out that section and make a new parcel of it.
        // viewer -> sim
        // reliable
        {
        	ParcelDivide Low 211 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	West		F32		}
        		{	South		F32		}
        		{	East		F32		}
        		{	North		F32		}
        	}
        }
        '''

    def request_parcel_access_list(self, ):
        """ request an access list for the specified parcel """

        self.onParcelAccessListReply_received = self.packet_handler._register('ParcelAccessListReply')
        self.onParcelAccessListReply_received.subscribe(self.onParcelAccessListReply)

        pass

        '''
        // ParcelAccessListRequest
        {
        	ParcelAccessListRequest Low 215 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data	Single
        		{	SequenceID		S32		}
        		{	Flags			U32		}
        		{	LocalID			S32		}
        	}
        }
        '''

    def sendParcelAccessListRequest(self, ):
        """ send a ParcelAccessListRequest packet """

        pass

        '''
        // ParcelAccessListRequest
        {
        	ParcelAccessListRequest Low 215 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data	Single
        		{	SequenceID		S32		}
        		{	Flags			U32		}
        		{	LocalID			S32		}
        	}
        }
        '''

    def onParcelAccessListReply(self, packet):
        """ parse and handle a ParcelAccessListReply packet """

        self.onParcelAccessListReply_received.unsubscribe(self.onParcelAccessListReply)

        pass

        '''
        // sim -> viewer
        // ParcelAccessListReply
        {
        	ParcelAccessListReply Low 216 Trusted Zerocoded
        	{
        		Data	Single
        		{	AgentID			LLUUID	}
        		{	SequenceID		S32		}
        		{	Flags			U32		}
        		{	LocalID			S32		}
        	}
        	{
        		List	Variable
        		{	ID			LLUUID		}
        		{	Time		S32			} // time_t
        		{	Flags		U32			}
        	}
        }
        '''

class Parcel(object):
    """ a representation of a parcel """

    def __init__(self, region, agent, RequestResult = None, SequenceID = None, SnapSelection = None, SelfCount = None, OtherCount = None, PublicCount = None, LocalID = None, OwnerID = None, IsGroupOwned = None, AuctionID = None, ClaimDate = None, ClaimPrice = None, RentPrice = None, AABBMin = None, AABBMax = None, Bitmap = None, Area = None, Status = None, SimWideMaxPrims = None, SimWideTotalPrims = None, MaxPrims = None, TotalPrims = None, OwnerPrims = None, GroupPrims = None, OtherPrims = None, SelectedPrims = None, ParcelPrimBonus = None, OtherCleanTime = None, ParcelFlags = None, SalePrice = None, Name = None, Desc = None, MusicURL = None, MediaURL = None, MediaID = None, MediaAutoScale = None, GroupID = None, PassPrice = None, PassHours = None, Category = None, AuthBuyerID = None, SnapshotID = None, UserLocation = None, UserLookAt = None, LandingType = None, RegionPushOverride = None, RegionDenyAnonymous = None, RegionDenyIdentified = None, RegionDenyTransacted = None, RegionDenyAgeUnverified = None, ParcelID = None, ActualArea = None, BillableArea = None, Flags = None, GlobalX = None, GlobalY = None, GlobalZ = None, SimName = None, Dwell = None, settings = None):
        """ initialize a representation of a parcel. the data is currently being populated directly from the ParcelProperties message """

        # allow the settings to be passed in
        # otherwise, grab the defaults
        if settings != None:
            self.settings = settings
        else:
            from pyogp.lib.base.settings import Settings
            self.settings = Settings()

        self.region = region
        self.agent = agent

        # mapping values from the ParcelProperties message
        # not all properties will ultimately live here, but for now
        # mapping all of them will do

        # from ParcelInfoReply
        self.ParcelID = ParcelID
        self.OwnerID = OwnerID
        self.ActualArea = ActualArea
        self.BillableArea = BillableArea
        self.Flags = Flags
        self.GlobalX = GlobalX
        self.GlobalY = GlobalY
        self.GlobalZ = GlobalZ
        self.SimName = SimName
        self.Dwell = Dwell
        self.AuctionID = AuctionID

        # from ParcelProperties
        self.RequestResult = RequestResult 
        self.SequenceID = SequenceID 
        self.SnapSelection = SnapSelection 
        self.SelfCount = SelfCount 
        self.OtherCount = OtherCount 
        self.PublicCount = PublicCount 
        self.LocalID = LocalID 
        self.OwnerID = OwnerID 
        self.IsGroupOwned = IsGroupOwned 
        self.AuctionID = AuctionID 
        self.ClaimDate = ClaimDate 
        self.ClaimPrice = ClaimPrice 
        self.RentPrice = RentPrice 
        self.AABBMin = AABBMin 
        self.AABBMax = AABBMax 
        self.Bitmap = Bitmap 
        self.Area = Area 
        self.Status = Status 
        self.SimWideMaxPrims = SimWideMaxPrims 
        self.SimWideTotalPrims = SimWideTotalPrims 
        self.MaxPrims = MaxPrims 
        self.TotalPrims = TotalPrims 
        self.OwnerPrims = OwnerPrims 
        self.GroupPrims = GroupPrims 
        self.OtherPrims = OtherPrims 
        self.SelectedPrims = SelectedPrims 
        self.ParcelPrimBonus = ParcelPrimBonus 
        self.OtherCleanTime = OtherCleanTime 
        self.ParcelFlags = ParcelFlags 
        self.SalePrice = SalePrice 
        self.Name = Name 
        self.Desc = Desc 
        self.MusicURL = MusicURL 
        self.MediaURL = MediaURL 
        self.MediaID = MediaID 
        self.MediaAutoScale = MediaAutoScale 
        self.GroupID = GroupID 
        self.PassPrice = PassPrice 
        self.PassHours = PassHours 
        self.Category = Category 
        self.AuthBuyerID = AuthBuyerID 
        self.SnapshotID = SnapshotID 
        self.UserLocation = UserLocation 
        self.UserLookAt = UserLookAt 
        self.LandingType = LandingType 
        self.RegionPushOverride = RegionPushOverride 
        self.RegionDenyAnonymous = RegionDenyAnonymous 
        self.RegionDenyIdentified = RegionDenyIdentified 
        self.RegionDenyTransacted = RegionDenyTransacted 
        self.RegionDenyAgeUnverified = RegionDenyAgeUnverified 

    def _update_properties(self, parcel_properties):
        """ update a parcel's properties via a dictionary """

        for attribute in parcel_properties:

            setattr(self, attribute, parcel_properties[attribute])

    def return_objects(self, ):
        """ return the specified objects for this parcel """

        pass

        '''
        // ParcelReturnObjects
        // viewer -> sim
        // reliable
        {
        	ParcelReturnObjects Low 199 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def set_other_clean_time(self, ):
        """ sends a SetOtherCleanTime packet for this parcel """

        pass

        '''
        // ParcelSetOtherCleanTime
        // viewer -> sim
        // reliable
        {
        	ParcelSetOtherCleanTime Low 200 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	OtherCleanTime	S32				}
        	}
        }
        '''

    def disable_objects(self, ):
        """ set objects nonphysical and disable scripts for this parcel """

        pass

        '''
        // Disable makes objects nonphysical and turns off their scripts.
        // ParcelDisableObjects
        // viewer -> sim
        // reliable
        {
        	ParcelDisableObjects Low 201 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		TaskIDs			Variable
        		{	TaskID			LLUUID			}
        	}
        	{
        		OwnerIDs			Variable
        		{	OwnerID			LLUUID			}
        	}
        }
        '''

    def select_objects(self, ):
        """ selects the specified objects for this parcel """

        pass

        '''
        // ParcelSelectObjects
        // viewer -> sim
        // reliable
        {
        	ParcelSelectObjects Low 202 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		ParcelData			Single
        		{	LocalID			S32				}
        		{	ReturnType		U32				}
        	}
        	{
        		ReturnIDs			Variable
        		{	ReturnID		LLUUID	}
        	}
        }
        '''

    def deed_to_group(self, ):
        """ deed this parcel to a group """

        pass

        '''
        // ParcelDeedToGroup - deed a patch of land to a group
        // viewer -> sim
        // reliable
        {
        	ParcelDeedToGroup Low 207 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data				Single
        		{	GroupID			LLUUID	}
        		{	LocalID			S32		}	// parcel id
        	}
        }
        '''

    def reclaim(self, ):
        """ reclaim this parcel"""

        pass

        '''
        // reserved for when island owners force re-claim parcel
        {
        	ParcelReclaim Low 208 NotTrusted Unencoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data				Single
        		{	LocalID			S32		}	// parcel id
        	}
        }
        '''

    def claim(self, ):
        """ change the owner of a parcel """

        pass

        '''
        // ParcelClaim - change the owner of a patch of land
        // viewer -> sim
        // reliable
        {
        	ParcelClaim Low 209 NotTrusted Zerocoded
        	{
        		AgentData			Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data				Single
        		{	GroupID			LLUUID	}
        		{	IsGroupOwned	BOOL 	}
        		{	Final			BOOL	} // true if buyer is in tier
        	}
        	{
        		ParcelData			Variable
        		{	West			F32		}
        		{	South			F32		}
        		{	East			F32		}
        		{	North			F32		}
        	}
        }
        '''

    def release(self, ):
        """ release this parcel to the public """

        pass

        '''
        // ParcelRelease
        // Release a parcel to public
        // viewer -> sim
        // reliable
        {
        	ParcelRelease Low 212 NotTrusted Unencoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data			Single
        		{	LocalID			S32		}	// parcel ID
        	}
        }
        '''

    def buy(self, ):
        """ buy this parcel """

        pass

        '''
        // ParcelBuy - change the owner of a patch of land.
        // viewer -> sim
        // reliable
        {
        	ParcelBuy Low 213 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data			Single
        		{	GroupID			LLUUID	}
        		{	IsGroupOwned	BOOL 	}
        		{	RemoveContribution BOOL	}
        		{	LocalID			S32		}
        		{	Final			BOOL	} // true if buyer is in tier
        	}
        	{
        		ParcelData		Single
        		{	Price			S32		}
        		{	Area			S32		}
        	}
        }
        '''

    def godforce_owner(self, ):
        """ god force own this parcel """

        pass

        '''
        // ParcelGodForceOwner Unencoded
        {
        	ParcelGodForceOwner	Low	214 NotTrusted Zerocoded
        	{
        		AgentData		Single
        		{	AgentID			LLUUID	}
        		{	SessionID		LLUUID	}
        	}
        	{
        		Data			Single
        		{	OwnerID			LLUUID	}
        		{	LocalID			S32		}	// parcel ID
        	}
        }
        '''

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""
